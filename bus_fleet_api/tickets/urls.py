"""
URL patterns for the tickets app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, BookingViewSet, ReceiptViewSet, DiscountViewSet

router = DefaultRouter()
router.register('tickets', TicketViewSet, basename='ticket')
router.register('bookings', BookingViewSet, basename='booking')
router.register('receipts', ReceiptViewSet, basename='receipt')
router.register('discounts', DiscountViewSet, basename='discount')

urlpatterns = [
    path('', include(router.urls)),
]
