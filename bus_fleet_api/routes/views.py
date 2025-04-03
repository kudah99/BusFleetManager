"""
Views for the routes app.
"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Route, RouteStop, RouteSchedule
from .serializers import (
    RouteSerializer, RouteDetailSerializer, 
    RouteStopSerializer, RouteScheduleSerializer
)
from common.permissions import IsStaffOrHigher, IsSameCompanyOnly


class RouteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for routes.
    """
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'type', 'frequency']
    search_fields = ['name', 'code', 'origin', 'destination']
    ordering_fields = ['name', 'code', 'distance', 'duration', 'base_price', 'created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RouteDetailSerializer
        return RouteSerializer

    def get_queryset(self):
        """
        Filter queryset to only include routes from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Route.objects.none()
        return Route.objects.filter(company=user.company)

    @action(detail=True, methods=['get'])
    def stops(self, request, pk=None):
        """
        Get all stops for a specific route.
        """
        route = self.get_object()
        queryset = RouteStop.objects.filter(route=route).order_by('stop_number')
        serializer = RouteStopSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def schedules(self, request, pk=None):
        """
        Get all schedules for a specific route.
        """
        route = self.get_object()
        queryset = RouteSchedule.objects.filter(route=route)
        serializer = RouteScheduleSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class RouteStopViewSet(viewsets.ModelViewSet):
    """
    API endpoint for route stops.
    """
    serializer_class = RouteStopSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['route', 'city', 'country', 'is_origin', 'is_destination']
    search_fields = ['name', 'code', 'address', 'city']
    ordering_fields = ['stop_number', 'name', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include route stops from the user's company.
        """
        user = self.request.user
        if not user.company:
            return RouteStop.objects.none()
        return RouteStop.objects.filter(company=user.company)


class RouteScheduleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for route schedules.
    """
    serializer_class = RouteScheduleSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['route', 'is_active', 'start_date', 'end_date']
    ordering_fields = ['departure_time', 'arrival_time', 'start_date', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include route schedules from the user's company.
        """
        user = self.request.user
        if not user.company:
            return RouteSchedule.objects.none()
        return RouteSchedule.objects.filter(company=user.company)
