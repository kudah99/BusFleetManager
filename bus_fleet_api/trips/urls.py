"""
URL patterns for the trips app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, TripEventViewSet, TripStopViewSet

router = DefaultRouter()
router.register('trips', TripViewSet, basename='trip')
router.register('events', TripEventViewSet, basename='trip-event')
router.register('stops', TripStopViewSet, basename='trip-stop')

urlpatterns = [
    path('', include(router.urls)),
]
