"""
Views for the trips app.
"""
from datetime import datetime
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Trip, TripEvent, TripStop, TripStatus
from .serializers import TripSerializer, TripEventSerializer, TripStopSerializer
from common.permissions import IsStaffOrHigher, IsSameCompanyOnly, IsDriverOrHigher


class TripViewSet(viewsets.ModelViewSet):
    """
    API endpoint for trips.
    """
    serializer_class = TripSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['route', 'bus', 'driver', 'conductor', 'status', 'departure_date']
    search_fields = ['route__name', 'bus__registration_number', 'driver__first_name', 'driver__last_name']
    ordering_fields = ['departure_date', 'departure_time', 'status', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include trips from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Trip.objects.none()
        return Trip.objects.filter(company=user.company)

    @action(detail=True, methods=['post'], url_path='start-trip')
    def start_trip(self, request, pk=None):
        """
        Start a trip by updating its status to active and setting the actual departure time.
        """
        trip = self.get_object()
        
        if trip.status != TripStatus.SCHEDULED:
            return Response(
                {'detail': f'Trip is not in scheduled status (current status: {trip.status})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trip.status = TripStatus.ACTIVE
        trip.actual_departure = timezone.now()
        trip.save()
        
        # Create a departure event
        TripEvent.objects.create(
            company=trip.company,
            trip=trip,
            event_type="Departure",
            timestamp=trip.actual_departure,
            description="Trip started",
            recorded_by=trip.driver
        )
        
        return Response({'detail': 'Trip started successfully'})
        
    @action(detail=True, methods=['post'], url_path='complete-trip')
    def complete_trip(self, request, pk=None):
        """
        Complete a trip by updating its status to completed and setting the actual arrival time.
        """
        trip = self.get_object()
        
        if trip.status != TripStatus.ACTIVE:
            return Response(
                {'detail': f'Trip is not in active status (current status: {trip.status})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trip.status = TripStatus.COMPLETED
        trip.actual_arrival = timezone.now()
        trip.save()
        
        # Create an arrival event
        TripEvent.objects.create(
            company=trip.company,
            trip=trip,
            event_type="Arrival",
            timestamp=trip.actual_arrival,
            description="Trip completed",
            recorded_by=trip.driver
        )
        
        return Response({'detail': 'Trip completed successfully'})
        
    @action(detail=True, methods=['post'], url_path='cancel-trip')
    def cancel_trip(self, request, pk=None):
        """
        Cancel a trip by updating its status to cancelled.
        """
        trip = self.get_object()
        
        if trip.status not in [TripStatus.SCHEDULED, TripStatus.DELAYED]:
            return Response(
                {'detail': f'Trip cannot be cancelled (current status: {trip.status})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        if not reason:
            return Response(
                {'detail': 'Cancellation reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trip.status = TripStatus.CANCELLED
        trip.cancellation_reason = reason
        trip.save()
        
        return Response({'detail': 'Trip cancelled successfully'})
        
    @action(detail=True, methods=['post'], url_path='delay-trip')
    def delay_trip(self, request, pk=None):
        """
        Mark a trip as delayed.
        """
        trip = self.get_object()
        
        if trip.status not in [TripStatus.SCHEDULED, TripStatus.ACTIVE]:
            return Response(
                {'detail': f'Trip cannot be marked as delayed (current status: {trip.status})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        if not reason:
            return Response(
                {'detail': 'Delay reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trip.status = TripStatus.DELAYED
        trip.delay_reason = reason
        trip.save()
        
        # Create a delay event
        TripEvent.objects.create(
            company=trip.company,
            trip=trip,
            event_type="Delay",
            timestamp=timezone.now(),
            description=reason,
            recorded_by=trip.driver
        )
        
        return Response({'detail': 'Trip marked as delayed successfully'})

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """
        Get all events for a specific trip.
        """
        trip = self.get_object()
        queryset = TripEvent.objects.filter(trip=trip)
        serializer = TripEventSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stops(self, request, pk=None):
        """
        Get all stops for a specific trip.
        """
        trip = self.get_object()
        queryset = TripStop.objects.filter(trip=trip)
        serializer = TripStopSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Get all trips for today.
        """
        today = timezone.now().date()
        queryset = self.get_queryset().filter(departure_date=today)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get all upcoming trips.
        """
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            departure_date__gte=today, 
            status__in=[TripStatus.SCHEDULED, TripStatus.DELAYED]
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active trips.
        """
        queryset = self.get_queryset().filter(status=TripStatus.ACTIVE)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TripEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for trip events.
    """
    serializer_class = TripEventSerializer
    permission_classes = [IsDriverOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['trip', 'event_type', 'recorded_by']
    search_fields = ['description', 'location']
    ordering_fields = ['timestamp', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include trip events from the user's company.
        """
        user = self.request.user
        if not user.company:
            return TripEvent.objects.none()
        return TripEvent.objects.filter(company=user.company)


class TripStopViewSet(viewsets.ModelViewSet):
    """
    API endpoint for trip stops.
    """
    serializer_class = TripStopSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['trip', 'route_stop', 'status']
    search_fields = ['notes']
    ordering_fields = ['scheduled_arrival', 'scheduled_departure', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include trip stops from the user's company.
        """
        user = self.request.user
        if not user.company:
            return TripStop.objects.none()
        return TripStop.objects.filter(company=user.company)
        
    @action(detail=True, methods=['post'], url_path='arrive')
    def arrive(self, request, pk=None):
        """
        Mark a trip stop as arrived.
        """
        trip_stop = self.get_object()
        
        if trip_stop.status != "Pending":
            return Response(
                {'detail': f'Trip stop is not in pending status (current status: {trip_stop.status})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trip_stop.status = "Arrived"
        trip_stop.actual_arrival = timezone.now()
        trip_stop.save()
        
        # Create a stop event
        TripEvent.objects.create(
            company=trip_stop.company,
            trip=trip_stop.trip,
            event_type="Stop",
            timestamp=trip_stop.actual_arrival,
            description=f"Arrived at {trip_stop.route_stop.name}",
            location=trip_stop.route_stop.name,
            latitude=trip_stop.route_stop.latitude,
            longitude=trip_stop.route_stop.longitude,
            recorded_by=trip_stop.trip.driver
        )
        
        return Response({'detail': 'Trip stop marked as arrived'})

    @action(detail=True, methods=['post'], url_path='depart')
    def depart(self, request, pk=None):
        """
        Mark a trip stop as departed.
        """
        trip_stop = self.get_object()
        
        if trip_stop.status != "Arrived":
            return Response(
                {'detail': f'Trip stop is not in arrived status (current status: {trip_stop.status})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trip_stop.status = "Departed"
        trip_stop.actual_departure = timezone.now()
        
        # Update passenger counts if provided
        if 'passengers_boarding' in request.data:
            trip_stop.passengers_boarding = request.data['passengers_boarding']
            
        if 'passengers_alighting' in request.data:
            trip_stop.passengers_alighting = request.data['passengers_alighting']
            
        trip_stop.save()
        
        # Create a stop event for departure
        TripEvent.objects.create(
            company=trip_stop.company,
            trip=trip_stop.trip,
            event_type="Stop",
            timestamp=trip_stop.actual_departure,
            description=f"Departed from {trip_stop.route_stop.name}",
            location=trip_stop.route_stop.name,
            latitude=trip_stop.route_stop.latitude,
            longitude=trip_stop.route_stop.longitude,
            recorded_by=trip_stop.trip.driver
        )
        
        return Response({'detail': 'Trip stop marked as departed'})
