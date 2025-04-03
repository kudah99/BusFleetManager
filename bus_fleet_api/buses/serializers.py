"""
Serializers for the buses app.
"""
from rest_framework import serializers
from .models import Bus, BusMaintenance, BusExpense, BusDocument, Location


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for Location model.
    """
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)


class BusSerializer(serializers.ModelSerializer):
    """
    Serializer for Bus model.
    """
    assigned_driver_details = serializers.SerializerMethodField(read_only=True)
    current_location_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bus
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def get_assigned_driver_details(self, obj):
        if obj.assigned_driver:
            return {
                'id': obj.assigned_driver.id,
                'name': f"{obj.assigned_driver.first_name} {obj.assigned_driver.last_name}"
            }
        return None

    def get_current_location_details(self, obj):
        if obj.current_location:
            return {
                'id': obj.current_location.id,
                'name': obj.current_location.name,
                'address': obj.current_location.address
            }
        return None

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)


class BusMaintenanceSerializer(serializers.ModelSerializer):
    """
    Serializer for BusMaintenance model.
    """
    bus_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BusMaintenance
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def get_bus_details(self, obj):
        return {
            'id': obj.bus.id,
            'registration_number': obj.bus.registration_number,
            'model': obj.bus.model
        }

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)

    def validate_bus(self, value):
        # Ensure bus belongs to the same company
        if value.company != self.context['request'].user.company:
            raise serializers.ValidationError("Bus does not belong to your company")
        return value


class BusExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer for BusExpense model.
    """
    bus_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BusExpense
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def get_bus_details(self, obj):
        return {
            'id': obj.bus.id,
            'registration_number': obj.bus.registration_number,
            'model': obj.bus.model
        }

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)

    def validate_bus(self, value):
        # Ensure bus belongs to the same company
        if value.company != self.context['request'].user.company:
            raise serializers.ValidationError("Bus does not belong to your company")
        return value


class BusDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for BusDocument model.
    """
    bus_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BusDocument
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def get_bus_details(self, obj):
        return {
            'id': obj.bus.id,
            'registration_number': obj.bus.registration_number,
            'model': obj.bus.model
        }

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)

    def validate_bus(self, value):
        # Ensure bus belongs to the same company
        if value.company != self.context['request'].user.company:
            raise serializers.ValidationError("Bus does not belong to your company")
        return value
