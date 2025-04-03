"""
Serializers for the accounts app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Company, UserRole, UserStatus

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for Company model.
    """
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'business_name', 'registration_number', 'tax_id',
            'address', 'city', 'state', 'country', 'zip_code', 'phone',
            'email', 'website', 'logo_url', 'is_active', 'subscription_plan',
            'subscription_expires', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    company = CompanySerializer(read_only=True)
    company_id = serializers.UUIDField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'confirm_password', 'first_name', 'last_name',
            'role', 'status', 'phone', 'company', 'company_id', 'employee_id',
            'last_login', 'email_verified', 'phone_verified', 'two_factor_enabled',
            'profile_image_url', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_login', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate that password and confirm_password match.
        """
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({'confirm_password': "Passwords don't match"})
            validate_password(data['password'])
        return data

    def create(self, validated_data):
        """
        Create a new user with encrypted password.
        """
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        company_id = validated_data.pop('company_id', None)
        
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
                validated_data['company'] = company
            except Company.DoesNotExist:
                raise serializers.ValidationError({'company_id': "Company with this ID does not exist"})
        
        user = User.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        return user

    def update(self, instance, validated_data):
        """
        Update a user, correctly handling the password.
        """
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        company_id = validated_data.pop('company_id', None)
        
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
                validated_data['company'] = company
            except Company.DoesNotExist:
                raise serializers.ValidationError({'company_id': "Company with this ID does not exist"})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    company_name = serializers.CharField(write_only=True, required=True)
    business_name = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'confirm_password', 'first_name', 'last_name',
            'phone', 'company_name', 'business_name'
        ]

    def validate(self, data):
        """
        Validate that password and confirm_password match.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': "Passwords don't match"})
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        """
        Create a new company and admin user.
        """
        company_name = validated_data.pop('company_name')
        business_name = validated_data.pop('business_name')
        validated_data.pop('confirm_password')
        
        # Create company
        company = Company.objects.create(
            name=company_name,
            business_name=business_name
        )
        
        # Create user with admin role
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone'),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            company=company
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        """
        Validate that new_password and confirm_password match.
        """
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': "Passwords don't match"})
        validate_password(data['new_password'])
        return data
