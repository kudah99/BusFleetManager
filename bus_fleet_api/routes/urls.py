"""
URL patterns for the routes app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, RouteStopViewSet, RouteScheduleViewSet

router = DefaultRouter()
router.register('routes', RouteViewSet, basename='route')
router.register('stops', RouteStopViewSet, basename='route-stop')
router.register('schedules', RouteScheduleViewSet, basename='route-schedule')

urlpatterns = [
    path('', include(router.urls)),
]
