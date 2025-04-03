"""
API URL configuration for the bus fleet management system.
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    API root endpoint, providing links to other endpoints.
    """
    return Response({
        'auth_login': reverse('token_obtain_pair', request=request, format=format),
        'auth_refresh': reverse('token_refresh', request=request, format=format),
        'accounts': '/api/accounts/',
        'buses': '/api/buses/',
        'routes': '/api/routes/',
        'employees': '/api/employees/',
        'trips': '/api/trips/',
        'tickets': '/api/tickets/',
    })


urlpatterns = [
    # API Documentation
    path('', api_root, name='api-root'),
    
    # Authentication endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App-specific endpoints
    path('accounts/', include('accounts.urls')),
    path('buses/', include('buses.urls')),
    path('routes/', include('routes.urls')),
    path('employees/', include('employees.urls')),
    path('trips/', include('trips.urls')),
    path('tickets/', include('tickets.urls')),
]
