"""
URL patterns for the buses app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BusViewSet, BusMaintenanceViewSet, 
    BusExpenseViewSet, BusDocumentViewSet, LocationViewSet
)

router = DefaultRouter()
router.register('buses', BusViewSet, basename='bus')
router.register('maintenance', BusMaintenanceViewSet, basename='bus-maintenance')
router.register('expenses', BusExpenseViewSet, basename='bus-expense')
router.register('documents', BusDocumentViewSet, basename='bus-document')
router.register('locations', LocationViewSet, basename='location')

urlpatterns = [
    path('', include(router.urls)),
]
