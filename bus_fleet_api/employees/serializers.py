"""
Serializers for the employees app.
"""
from rest_framework import serializers
from .models import Employee, Document, Leave, Attendance
from django.contrib.auth import get_user_model

User = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model.
    """
    manager_name = serializers.SerializerMethodField(read_only=True)
    user_email = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def get_manager_name(self, obj):
        if obj.manager:
            return f"{obj.manager.first_name} {obj.manager.last_name}"
        return None
        
    def get_user_email(self, obj):
        if obj.user:
            return obj.user.email
        return None

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)
        
    def validate_manager(self, value):
        if value:
            # Ensure manager belongs to the same company
            if value.company != self.context['request'].user.company:
                raise serializers.ValidationError("Manager does not belong to your company")
        return value
        
    def validate_user(self, value):
        if value:
            # Ensure user belongs to the same company
            if value.company != self.context['request'].user.company:
                raise serializers.ValidationError("User does not belong to your company")
            
            # Check if user is already linked to another employee
            if hasattr(value, 'employee') and value.employee is not None:
                if not self.instance or self.instance.id != value.employee.id:
                    raise serializers.ValidationError("User is already linked to another employee")
        return value


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for Document model.
    """
    employee_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)
        
    def validate_employee(self, value):
        # Ensure employee belongs to the same company
        if value.company != self.context['request'].user.company:
            raise serializers.ValidationError("Employee does not belong to your company")
        return value


class LeaveSerializer(serializers.ModelSerializer):
    """
    Serializer for Leave model.
    """
    employee_name = serializers.SerializerMethodField(read_only=True)
    approved_by_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Leave
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
        
    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}"
        return None

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)
        
    def validate_employee(self, value):
        # Ensure employee belongs to the same company
        if value.company != self.context['request'].user.company:
            raise serializers.ValidationError("Employee does not belong to your company")
        return value
        
    def validate_approved_by(self, value):
        if value:
            # Ensure approver belongs to the same company
            if value.company != self.context['request'].user.company:
                raise serializers.ValidationError("Approver does not belong to your company")
        return value


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model.
    """
    employee_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)
        
    def validate_employee(self, value):
        # Ensure employee belongs to the same company
        if value.company != self.context['request'].user.company:
            raise serializers.ValidationError("Employee does not belong to your company")
        return value


class EmployeeUserLinkSerializer(serializers.Serializer):
    """
    Serializer for linking an employee to a user account.
    """
    user_id = serializers.UUIDField(required=True)
    
    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            
            # Ensure user belongs to the same company
            if user.company != self.context['request'].user.company:
                raise serializers.ValidationError("User does not belong to your company")
            
            # Check if user is already linked to another employee
            if hasattr(user, 'employee') and user.employee is not None:
                raise serializers.ValidationError("User is already linked to another employee")
                
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this ID does not exist")
