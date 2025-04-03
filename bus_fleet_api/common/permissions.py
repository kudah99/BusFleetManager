"""
Custom permissions for the bus fleet management API.
"""
from rest_framework import permissions
from accounts.models import UserRole


class IsCompanyAdmin(permissions.BasePermission):
    """
    Permission that allows access only to company administrators.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN


class IsCompanyManagerOrAdmin(permissions.BasePermission):
    """
    Permission that allows access to company managers and administrators.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [UserRole.ADMIN, UserRole.MANAGER]


class IsStaffOrHigher(permissions.BasePermission):
    """
    Permission that allows access to staff and higher roles.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF
        ]


class IsSameCompanyOnly(permissions.BasePermission):
    """
    Permission that restricts access to objects belonging to the user's company.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is authenticated and has a company
        if not request.user.is_authenticated or not hasattr(request.user, 'company'):
            return False

        # Check if the object has a company attribute
        if hasattr(obj, 'company'):
            return obj.company == request.user.company
            
        # Check if the object has a company_id attribute
        if hasattr(obj, 'company_id'):
            return obj.company_id == request.user.company.id
            
        return False


class IsDriverOrHigher(permissions.BasePermission):
    """
    Permission that allows access to drivers and higher roles.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF, UserRole.DRIVER
        ]


class IsConductorOrHigher(permissions.BasePermission):
    """
    Permission that allows access to conductors and higher roles.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF, UserRole.CONDUCTOR
        ]


class IsCustomer(permissions.BasePermission):
    """
    Permission that allows access to customers only.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.CUSTOMER
