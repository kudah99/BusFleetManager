"""
Serializers for the trips app.
"""
from rest_framework import serializers
from .models import Trip, TripEvent, TripStop
from routes.serializers import RouteSerializer
from employees.models import Employee, EmployeeRole
from buses.models import Bus, BusStatus


class TripSerializer(serializers.ModelSerializer):
    """
    Serializer for Trip model.
    """
    route_details = serializers.SerializerMethodField(read_only=True)
    bus_details = serializers.SerializerMethodField(read_only=True)
    driver_details = serializers.SerializerMethodField(read_only=True)
    conductor_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def get_route_details(self, obj):
        return {
            'id': obj.route.id,
            'name': obj.route.name,
            'origin': obj.route.origin,
            'destination': obj.route.destination
        }
        
    def get_bus_details(self, obj):
        return {
            'id': obj.bus.id,
            'registration_number': obj.bus.registration_number,
            'model': obj.bus.model
        }
        
    def get_driver_details(self, obj):
        return {
            'id': obj.driver.id,
            'name': f"{obj.driver.first_name} {obj.driver.last_name}"
        }
        
    def get_conductor_details(self, obj):
        if obj.conductor:
            return {
                'id': obj.conductor.id,
                'name': f"{obj.conductor.first_name} {obj.conductor.last_name}"
            }
        return None

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)
        
    def validate(self, data):
        # Ensure route, bus, driver, and conductor belong to the same company
        company = self.context['request'].user.company
        
        if data.get('route').company != company:
            raise serializers.ValidationError({'route': "Route does not belong to your company"})
            
        if data.get('bus').company != company:
            raise serializers.ValidationError({'bus': "Bus does not belong to your company"})
            
        if data.get('driver').company != company:
            raise serializers.ValidationError({'driver': "Driver does not belong to your company"})
            
        if data.get('conductor') and data.get('conductor').company != company:
            raise serializers.ValidationError({'conductor': "Conductor does not belong to your company"})
            
        # Ensure bus is active
        if data.get('bus').status != BusStatus.ACTIVE:
            raise serializers.ValidationError({'bus': f"Bus is not active (current status: {data.get('bus').status})"})
            
        # Ensure driver is a driver
        if data.get('driver').role != EmployeeRole.DRIVER:
            raise serializers.ValidationError({'driver': "Selected employee is not a driver"})
            
        # Ensure conductor is a conductor
        if data.get('conductor') and data.get('conductor').role != EmployeeRole.CONDUCTOR:
            raise serializers.ValidationError({'conductor': "Selected employee is not a conductor"})
            
        # Ensure capacity is valid
        if data.get('capacity', 0) <= 0:
            raise serializers.ValidationError({'capacity': "Capacity must be greater than 0"})
            
        # Ensure departure date and time are before arrival date and time
        departure_datetime = datetime.combine(data.get('departure_date'), data.get('departure_time'))
        arrival_datetime = datetime.combine(data.get('arrival_date'), data.get('arrival_time'))
        
        if departure_datetime >= arrival_datetime:
            raise serializers.ValidationError(
                "Departure date and time must be before arrival date and time"
            )
            
        return data


class TripEventSerializer(serializers.ModelSerializer):
    """
    Serializer for TripEvent model.
    """
    trip_details = serializers.SerializerMethodField(read_only=True)
    recorded_by_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = TripEvent
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def get_trip_details(self, obj):
        return {
            'id': obj.trip.id,
            'route_name': obj.trip.route.name,
            'departure_date': obj.trip.departure_date,
            'departure_time': obj.trip.departure_time
        }
        
    def get_recorded_by_name(self, obj):
        if obj.recorded_by:
            return f"{obj.recorded_by.first_name} {obj.recorded_by.last_name}"
        return None

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)
        
    def validate_trip(self, value):
        # Ensure trip belongs to the same company
        if value.company != self.context['request'].user.company:
            raise serializers.ValidationError("Trip does not belong to your company")
        return value
        
    def validate_recorded_by(self, value):
        if value:
            # Ensure recorder belongs to the same company
            if value.company != self.context['request'].user.company:
                raise serializers.ValidationError("Recorder does not belong to your company")
        return value


class TripStopSerializer(serializers.ModelSerializer):
    """
    Serializer for TripStop model.
    """
    trip_details = serializers.SerializerMethodField(read_only=True)
    stop_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = TripStop
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def get_trip_details(self, obj):
        return {
            'id': obj.trip.id,
            'route_name': obj.trip.route.name,
            'departure_date': obj.trip.departure_date,
            'departure_time': obj.trip.departure_time
        }
        
    def get_stop_details(self, obj):
        return {
            'id': obj.route_stop.id,
            'name': obj.route_stop.name,
            'address': obj.route_stop.address,
            'stop_number': obj.route_stop.stop_number
        }

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)
        
    def validate(self, data):
        # Ensure trip and route_stop belong to the same company
        company = self.context['request'].user.company
        
        if data.get('trip').company != company:
            raise serializers.ValidationError({'trip': "Trip does not belong to your company"})
            
        if data.get('route_stop').company != company:
            raise serializers.ValidationError({'route_stop': "Route stop does not belong to your company"})
            
        # Ensure route_stop belongs to the trip's route
        if data.get('route_stop').route != data.get('trip').route:
            raise serializers.ValidationError({'route_stop': "Route stop does not belong to the trip's route"})
            
        # Ensure scheduled_departure is after scheduled_arrival
        if data.get('scheduled_departure') <= data.get('scheduled_arrival'):
            raise serializers.ValidationError("Scheduled departure must be after scheduled arrival")
            
        return data
