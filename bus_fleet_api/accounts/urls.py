"""
URL patterns for the accounts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, UserViewSet, RegisterView

router = DefaultRouter()
router.register('companies', CompanyViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]
