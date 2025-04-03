"""
Views for the accounts app.
"""
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import Company, UserRole
from .serializers import (
    CompanySerializer, UserSerializer, RegisterSerializer, PasswordChangeSerializer
)
from common.permissions import (
    IsCompanyAdmin, IsCompanyManagerOrAdmin, IsSameCompanyOnly
)

User = get_user_model()


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for companies.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdmin]

    def get_queryset(self):
        """
        Filter queryset to only include the user's company,
        unless the user is a system administrator.
        """
        user = self.request.user
        if user.is_superuser:
            return Company.objects.all()
        return Company.objects.filter(id=user.company.id)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyManagerOrAdmin, IsSameCompanyOnly]

    def get_queryset(self):
        """
        Filter queryset to only include users from the same company.
        """
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        if not user.company:
            return User.objects.none()
        return User.objects.filter(company=user.company)

    @action(detail=False, methods=['get'])
    def drivers(self, request):
        """
        Get all drivers within the company.
        """
        queryset = self.get_queryset().filter(role=UserRole.DRIVER)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def conductors(self, request):
        """
        Get all conductors within the company.
        """
        queryset = self.get_queryset().filter(role=UserRole.CONDUCTOR)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def staff(self, request):
        """
        Get all staff members within the company.
        """
        queryset = self.get_queryset().filter(role=UserRole.STAFF)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Get the current user's profile.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], url_path='update-profile')
    def update_profile(self, request):
        """
        Update the current user's profile.
        """
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """
        Change the current user's password.
        """
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Incorrect password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for company registration.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'detail': 'Company registered successfully. You can now log in.'},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
