"""
Serializers for the routes app.
"""
from rest_framework import serializers
from .models import Route, RouteStop, RouteSchedule


class RouteStopSerializer(serializers.ModelSerializer):
    """
    Serializer for RouteStop model.
    """
    class Meta:
        model = RouteStop
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)

    def validate_route(self, value):
        # Ensure route belongs to the same company
        if value.company != self.context['request'].user.company:
            raise serializers.ValidationError("Route does not belong to your company")
        return value


class RouteScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for RouteSchedule model.
    """
    class Meta:
        model = RouteSchedule
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)

    def validate_route(self, value):
        # Ensure route belongs to the same company
        if value.company != self.context['request'].user.company:
            raise serializers.ValidationError("Route does not belong to your company")
        return value

    def validate_days_of_week(self, value):
        # Ensure days_of_week is a list of integers between 0 and 6
        if not isinstance(value, list):
            raise serializers.ValidationError("Days of week must be a list")
        
        for day in value:
            if not isinstance(day, int) or day < 0 or day > 6:
                raise serializers.ValidationError(
                    "Each day must be an integer between 0 and 6 (0 is Monday, 6 is Sunday)"
                )
        
        return value


class RouteSerializer(serializers.ModelSerializer):
    """
    Serializer for Route model.
    """
    stops = RouteStopSerializer(many=True, read_only=True)
    schedules = RouteScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = '__all__'
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)


class RouteDetailSerializer(RouteSerializer):
    """
    Detailed serializer for Route model with stops and schedules.
    """
    class Meta(RouteSerializer.Meta):
        pass
