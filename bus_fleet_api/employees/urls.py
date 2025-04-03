"""
URL patterns for the employees app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, DocumentViewSet, LeaveViewSet, AttendanceViewSet

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee')
router.register('documents', DocumentViewSet, basename='document')
router.register('leaves', LeaveViewSet, basename='leave')
router.register('attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
]
