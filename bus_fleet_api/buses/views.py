"""
Views for the buses app.
"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Bus, BusMaintenance, BusExpense, BusDocument, Location
from .serializers import (
    BusSerializer, BusMaintenanceSerializer, 
    BusExpenseSerializer, BusDocumentSerializer, LocationSerializer
)
from common.permissions import IsStaffOrHigher, IsSameCompanyOnly
from rest_framework.decorators import action
from rest_framework.response import Response


class LocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for locations.
    """
    serializer_class = LocationSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_terminal', 'is_maintenance_facility', 'is_office', 'is_active', 'city', 'country']
    search_fields = ['name', 'address', 'city', 'country']
    ordering_fields = ['name', 'city', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include locations from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Location.objects.none()
        return Location.objects.filter(company=user.company)


class BusViewSet(viewsets.ModelViewSet):
    """
    API endpoint for buses.
    """
    serializer_class = BusSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'type', 'fuel_type', 'current_location', 'assigned_driver']
    search_fields = ['registration_number', 'license_plate', 'model', 'manufacturer']
    ordering_fields = ['registration_number', 'model', 'year', 'status', 'mileage', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include buses from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Bus.objects.none()
        return Bus.objects.filter(company=user.company)

    @action(detail=True, methods=['get'])
    def maintenance_records(self, request, pk=None):
        """
        Get all maintenance records for a specific bus.
        """
        bus = self.get_object()
        queryset = BusMaintenance.objects.filter(bus=bus)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = BusMaintenanceSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
            
        serializer = BusMaintenanceSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def expenses(self, request, pk=None):
        """
        Get all expenses for a specific bus.
        """
        bus = self.get_object()
        queryset = BusExpense.objects.filter(bus=bus)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = BusExpenseSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
            
        serializer = BusExpenseSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        Get all documents for a specific bus.
        """
        bus = self.get_object()
        queryset = BusDocument.objects.filter(bus=bus)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = BusDocumentSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
            
        serializer = BusDocumentSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)


class BusMaintenanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for bus maintenance records.
    """
    serializer_class = BusMaintenanceSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bus', 'status', 'date']
    search_fields = ['type', 'description', 'technician_name']
    ordering_fields = ['date', 'cost', 'status', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include maintenance records from the user's company.
        """
        user = self.request.user
        if not user.company:
            return BusMaintenance.objects.none()
        return BusMaintenance.objects.filter(company=user.company)


class BusExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for bus expenses.
    """
    serializer_class = BusExpenseSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bus', 'type', 'date']
    search_fields = ['description', 'payment_method']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include expenses from the user's company.
        """
        user = self.request.user
        if not user.company:
            return BusExpense.objects.none()
        return BusExpense.objects.filter(company=user.company)


class BusDocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for bus documents.
    """
    serializer_class = BusDocumentSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bus', 'type', 'issue_date', 'expiry_date']
    search_fields = ['name', 'notes']
    ordering_fields = ['issue_date', 'expiry_date', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include documents from the user's company.
        """
        user = self.request.user
        if not user.company:
            return BusDocument.objects.none()
        return BusDocument.objects.filter(company=user.company)
