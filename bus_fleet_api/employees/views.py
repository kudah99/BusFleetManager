"""
Views for the employees app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, Document, Leave, Attendance, EmployeeRole
from .serializers import (
    EmployeeSerializer, DocumentSerializer, 
    LeaveSerializer, AttendanceSerializer,
    EmployeeUserLinkSerializer
)
from common.permissions import IsStaffOrHigher, IsSameCompanyOnly
from django.contrib.auth import get_user_model

User = get_user_model()


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for employees.
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'status', 'department', 'country']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'license_number']
    ordering_fields = ['first_name', 'last_name', 'role', 'hire_date', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include employees from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Employee.objects.none()
        return Employee.objects.filter(company=user.company)

    @action(detail=False, methods=['get'])
    def drivers(self, request):
        """
        Get all drivers in the company.
        """
        queryset = self.get_queryset().filter(role=EmployeeRole.DRIVER)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def conductors(self, request):
        """
        Get all conductors in the company.
        """
        queryset = self.get_queryset().filter(role=EmployeeRole.CONDUCTOR)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        Get all documents for a specific employee.
        """
        employee = self.get_object()
        queryset = Document.objects.filter(employee=employee)
        serializer = DocumentSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def leaves(self, request, pk=None):
        """
        Get all leaves for a specific employee.
        """
        employee = self.get_object()
        queryset = Leave.objects.filter(employee=employee)
        serializer = LeaveSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """
        Get attendance records for a specific employee.
        """
        employee = self.get_object()
        queryset = Attendance.objects.filter(employee=employee)
        serializer = AttendanceSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'], url_path='link-user')
    def link_user(self, request, pk=None):
        """
        Link an employee to a user account.
        """
        employee = self.get_object()
        serializer = EmployeeUserLinkSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            
            try:
                user = User.objects.get(id=user_id)
                
                if employee.user:
                    return Response(
                        {'detail': 'Employee is already linked to a user account'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                employee.user = user
                employee.save()
                
                # Update the user's role based on employee role
                if employee.role:
                    if employee.role == EmployeeRole.DRIVER:
                        user.role = 'Driver'
                    elif employee.role == EmployeeRole.CONDUCTOR:
                        user.role = 'Conductor'
                    elif employee.role == EmployeeRole.ADMIN:
                        user.role = 'Admin'
                    elif employee.role == EmployeeRole.MANAGER:
                        user.role = 'Manager'
                    else:
                        user.role = 'Staff'
                    user.save()
                
                return Response({'detail': 'Employee linked to user successfully'})
            except User.DoesNotExist:
                return Response(
                    {'detail': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for employee documents.
    """
    serializer_class = DocumentSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'type', 'issue_date', 'expiry_date']
    search_fields = ['name', 'notes']
    ordering_fields = ['name', 'type', 'issue_date', 'expiry_date', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include documents from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Document.objects.none()
        return Document.objects.filter(company=user.company)


class LeaveViewSet(viewsets.ModelViewSet):
    """
    API endpoint for employee leaves.
    """
    serializer_class = LeaveSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'type', 'status', 'start_date', 'end_date']
    search_fields = ['reason', 'notes']
    ordering_fields = ['employee', 'type', 'start_date', 'status', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include leaves from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Leave.objects.none()
        return Leave.objects.filter(company=user.company)
        
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """
        Approve a leave request.
        """
        leave = self.get_object()
        
        if leave.status != "Pending":
            return Response(
                {'detail': 'Leave is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find the employee record of the current user
        try:
            approver = Employee.objects.get(user=request.user)
            
            leave.status = "Approved"
            leave.approved_by = approver
            leave.approved_at = timezone.now()
            leave.save()
            
            return Response({'detail': 'Leave approved successfully'})
        except Employee.DoesNotExist:
            return Response(
                {'detail': 'Approver must have an employee record'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """
        Reject a leave request.
        """
        leave = self.get_object()
        
        if leave.status != "Pending":
            return Response(
                {'detail': 'Leave is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave.status = "Rejected"
        leave.save()
        
        return Response({'detail': 'Leave rejected successfully'})


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for employee attendance.
    """
    serializer_class = AttendanceSerializer
    permission_classes = [IsStaffOrHigher, IsSameCompanyOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'date', 'status']
    search_fields = ['notes']
    ordering_fields = ['employee', 'date', 'status', 'created_at']

    def get_queryset(self):
        """
        Filter queryset to only include attendance records from the user's company.
        """
        user = self.request.user
        if not user.company:
            return Attendance.objects.none()
        return Attendance.objects.filter(company=user.company)
