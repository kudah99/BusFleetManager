"""
Views for the tickets app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

from .models import Ticket, Booking, Receipt, Discount, TicketStatus
from .serializers import (
    TicketSerializer, BookingSerializer, ReceiptSerializer, 
    DiscountSerializer, TicketCheckInSerializer
)
from common.permissions import (
    IsStaffOrHigher, IsSameCompanyOnly, IsCustomer, 
    IsCompanyManagerOrAdmin
)


class TicketViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tickets.
    """
    serializer_class = TicketSerializer
    permission_classes = [IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['trip', 'customer', 'status', 'type', 'payment_status']
    search_fields = ['booking_reference', 'passenger_name', 'passenger_email', 'passenger_phone']
    ordering_fields = ['issued_at', 'total_price', 'status', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include tickets from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Ticket.objects.none()
            
        # Get base queryset filtered by company
        queryset = Ticket.objects.filter(company=user.company)
        
        # If the user is a customer, only return their tickets
        if user.role == 'Customer':
            return queryset.filter(customer=user)
            
        return queryset

    @action(detail=True, methods=['post'], url_path='check-in')
    def check_in(self, request, pk=None):
        """
        Check in a ticket.
        """
        ticket = self.get_object()
        serializer = TicketCheckInSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            if ticket.status not in [TicketStatus.CONFIRMED, TicketStatus.RESERVED]:
                return Response(
                    {'detail': f'Ticket cannot be checked in (current status: {ticket.status})'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Update ticket status
            ticket.status = TicketStatus.CHECKED_IN
            ticket.checked_in_at = timezone.now()
            
            # Set who checked in the ticket
            if serializer.validated_data.get('checked_in_by'):
                employee = serializer.validated_data['checked_in_by'].employee
                ticket.checked_in_by = employee
            
            ticket.save()
            
            return Response({'detail': 'Ticket checked in successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        Cancel a ticket.
        """
        ticket = self.get_object()
        
        reason = request.data.get('reason', '')
        if not reason:
            return Response(
                {'detail': 'Cancellation reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if ticket.status not in [TicketStatus.RESERVED, TicketStatus.CONFIRMED]:
            return Response(
                {'detail': f'Ticket cannot be cancelled (current status: {ticket.status})'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Update ticket status
        ticket.status = TicketStatus.CANCELLED
        ticket.cancellation_reason = reason
        ticket.cancellation_date = timezone.now()
        ticket.save()
        
        # Decrease the trip's booked seats count
        if ticket.trip:
            ticket.trip.booked_seats = max(0, ticket.trip.booked_seats - 1)
            ticket.trip.save()
            
        return Response({'detail': 'Ticket cancelled successfully'})
        
    @action(detail=True, methods=['post'], url_path='refund')
    def refund(self, request, pk=None):
        """
        Refund a ticket.
        """
        ticket = self.get_object()
        
        if ticket.status != TicketStatus.CANCELLED:
            return Response(
                {'detail': 'Only cancelled tickets can be refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        refund_amount = request.data.get('refund_amount')
        if not refund_amount:
            return Response(
                {'detail': 'Refund amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Update ticket status
        ticket.status = TicketStatus.REFUNDED
        ticket.refund_amount = refund_amount
        ticket.refund_date = timezone.now()
        ticket.refund_reference = request.data.get('refund_reference', '')
        ticket.save()
        
        return Response({'detail': 'Ticket refunded successfully'})

    @action(detail=False, methods=['get'])
    def expired(self, request):
        """
        Get all expired tickets.
        """
        queryset = self.get_queryset().filter(
            Q(status=TicketStatus.RESERVED) & Q(expires_at__lt=timezone.now())
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Get all tickets for trips departing today.
        """
        today = timezone.now().date()
        queryset = self.get_queryset().filter(trip__departure_date=today)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for bookings.
    """
    serializer_class = BookingSerializer
    permission_classes = [IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'status', 'payment_status', 'source']
    search_fields = ['booking_reference', 'notes']
    ordering_fields = ['created_at', 'final_amount', 'status']

    def get_queryset(self):
        """
        Filter queryset to only include bookings from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Booking.objects.none()
            
        # Get base queryset filtered by company
        queryset = Booking.objects.filter(company=user.company)
        
        # If the user is a customer, only return their bookings
        if user.role == 'Customer':
            return queryset.filter(customer=user)
            
        return queryset

    @action(detail=True, methods=['get'])
    def tickets(self, request, pk=None):
        """
        Get all tickets for a specific booking.
        """
        booking = self.get_object()
        queryset = Ticket.objects.filter(booking=booking)
        serializer = TicketSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def receipts(self, request, pk=None):
        """
        Get all receipts for a specific booking.
        """
        booking = self.get_object()
        queryset = Receipt.objects.filter(booking=booking)
        serializer = ReceiptSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class ReceiptViewSet(viewsets.ModelViewSet):
    """
    API endpoint for receipts.
    """
    serializer_class = ReceiptSerializer
    permission_classes = [IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['booking', 'type', 'issued_by']
    search_fields = ['receipt_number', 'notes', 'booking__booking_reference']
    ordering_fields = ['issued_at', 'amount', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include receipts from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Receipt.objects.none()
            
        # Get base queryset filtered by company
        queryset = Receipt.objects.filter(company=user.company)
        
        # If the user is a customer, only return receipts for their bookings
        if user.role == 'Customer':
            return queryset.filter(booking__customer=user)
            
        return queryset


class DiscountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for discounts.
    """
    serializer_class = DiscountSerializer
    permission_classes = [IsCompanyManagerOrAdmin, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'type']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['start_date', 'end_date', 'value', 'usage_count', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include discounts from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Discount.objects.none()
        return Discount.objects.filter(company=user.company)

    @action(detail=True, methods=['post'], url_path='deactivate')
    def deactivate(self, request, pk=None):
        """
        Deactivate a discount code.
        """
        discount = self.get_object()
        
        if not discount.is_active:
            return Response(
                {'detail': 'Discount is already inactive'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        discount.is_active = False
        discount.save()
        
        return Response({'detail': 'Discount deactivated successfully'})

    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        """
        Activate a discount code.
        """
        discount = self.get_object()
        
        if discount.is_active:
            return Response(
                {'detail': 'Discount is already active'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        discount.is_active = True
        discount.save()
        
        return Response({'detail': 'Discount activated successfully'})

    @action(detail=False, methods=['get'], permission_classes=[IsSameCompanyOnly])
    def active(self, request):
        """
        Get all active discount codes.
        """
        now = timezone.now()
        queryset = self.get_queryset().filter(
            is_active=True,
            start_date__lte=now
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsSameCompanyOnly])
    def validate_code(self, request):
        """
        Validate a discount code.
        """
        code = request.data.get('code')
        if not code:
            return Response(
                {'detail': 'Discount code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            now = timezone.now()
            # Use filter instead of get with a Q object
            discount = self.get_queryset().filter(
                code=code,
                is_active=True,
                start_date__lte=now
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=now)
            ).get()
            
            # Check usage limit
            if discount.usage_limit and discount.usage_count >= discount.usage_limit:
                return Response(
                    {'detail': 'Discount code has reached its usage limit'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Return discount details
            serializer = self.get_serializer(discount)
            return Response(serializer.data)
            
        except Discount.DoesNotExist:
            return Response(
                {'detail': 'Invalid or expired discount code'},
                status=status.HTTP_404_NOT_FOUND
            )
