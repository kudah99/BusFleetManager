"""
Serializers for the tickets app.
"""
from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
import uuid
import random
import string

from .models import Ticket, Booking, Receipt, Discount
from trips.models import Trip, TripStatus
from django.contrib.auth import get_user_model

User = get_user_model()


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for Ticket model.
    """
    trip_details = serializers.SerializerMethodField(read_only=True)
    customer_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['id', 'company', 'booking_reference', 'created_at', 'updated_at']

    def get_trip_details(self, obj):
        return {
            'id': obj.trip.id,
            'route_name': obj.trip.route.name,
            'origin': obj.trip.route.origin,
            'destination': obj.trip.route.destination,
            'departure_date': obj.trip.departure_date,
            'departure_time': obj.trip.departure_time,
            'arrival_date': obj.trip.arrival_date,
            'arrival_time': obj.trip.arrival_time
        }
    
    def get_customer_details(self, obj):
        if obj.customer:
            return {
                'id': obj.customer.id,
                'name': f"{obj.customer.first_name} {obj.customer.last_name}",
                'email': obj.customer.email
            }
        return None

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        
        # Generate booking reference if not provided
        if 'booking_reference' not in validated_data:
            validated_data['booking_reference'] = self._generate_booking_reference()
            
        # Set default values
        trip = validated_data.get('trip')
        
        # Check if trip has available seats
        if trip.capacity <= trip.booked_seats:
            raise serializers.ValidationError({'trip': "No seats available for this trip"})
            
        # Check if trip is not cancelled or completed
        if trip.status in [TripStatus.CANCELLED, TripStatus.COMPLETED]:
            raise serializers.ValidationError({'trip': f"Cannot book ticket for a {trip.status.lower()} trip"})
            
        # Set expiration date (24 hours from now) if not set and status is RESERVED
        if validated_data.get('status') == 'Reserved' and 'expires_at' not in validated_data:
            validated_data['expires_at'] = timezone.now() + timezone.timedelta(hours=24)
            
        # Create the ticket
        ticket = super().create(validated_data)
        
        # Update the trip's booked seats count
        trip.booked_seats += 1
        trip.save()
        
        return ticket
        
    def update(self, instance, validated_data):
        # Check if status is changing to CANCELLED
        if (validated_data.get('status') == 'Cancelled' and 
            instance.status != 'Cancelled' and 
            'cancellation_reason' not in validated_data):
            raise serializers.ValidationError({'cancellation_reason': "Cancellation reason is required"})
            
        # Check if status is changing to CANCELLED
        if validated_data.get('status') == 'Cancelled' and instance.status != 'Cancelled':
            # Set cancellation date
            validated_data['cancellation_date'] = timezone.now()
            
            # Decrease the trip's booked seats count
            if instance.trip:
                instance.trip.booked_seats = max(0, instance.trip.booked_seats - 1)
                instance.trip.save()
                
        # Check if status is changing to CHECKED_IN
        if validated_data.get('status') == 'Checked In' and instance.status != 'Checked In':
            # Set checked in date
            validated_data['checked_in_at'] = timezone.now()
            
        return super().update(instance, validated_data)
        
    def validate_trip(self, value):
        # Ensure trip belongs to the same company
        if value.company != self.context['request'].user.company:
            raise serializers.ValidationError("Trip does not belong to your company")
        return value
        
    def validate_customer(self, value):
        if value:
            # Ensure customer belongs to the same company
            if value.company != self.context['request'].user.company:
                raise serializers.ValidationError("Customer does not belong to your company")
        return value
        
    def validate_checked_in_by(self, value):
        if value:
            # Ensure employee belongs to the same company
            if value.company != self.context['request'].user.company:
                raise serializers.ValidationError("Employee does not belong to your company")
        return value
        
    def _generate_booking_reference(self):
        """Generate a unique booking reference."""
        # Format: 2 letters + 6 digits
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        digits = ''.join(random.choices(string.digits, k=6))
        booking_reference = f"{letters}{digits}"
        
        # Check if it already exists
        while Ticket.objects.filter(booking_reference=booking_reference).exists():
            letters = ''.join(random.choices(string.ascii_uppercase, k=2))
            digits = ''.join(random.choices(string.digits, k=6))
            booking_reference = f"{letters}{digits}"
            
        return booking_reference


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model.
    """
    tickets = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ticket.objects.all(), required=False
    )
    customer_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['id', 'company', 'booking_reference', 'created_at', 'updated_at']

    def get_customer_details(self, obj):
        if obj.customer:
            return {
                'id': obj.customer.id,
                'name': f"{obj.customer.first_name} {obj.customer.last_name}",
                'email': obj.customer.email
            }
        return None

    @transaction.atomic
    def create(self, validated_data):
        # Remove tickets from validated data
        tickets_data = validated_data.pop('tickets', [])
        
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        
        # Generate booking reference if not provided
        if 'booking_reference' not in validated_data:
            validated_data['booking_reference'] = self._generate_booking_reference()
            
        # Create the booking
        booking = super().create(validated_data)
        
        # Associate tickets with the booking
        for ticket in tickets_data:
            if ticket.company != booking.company:
                raise serializers.ValidationError(
                    f"Ticket {ticket.booking_reference} does not belong to your company"
                )
            ticket.booking = booking
            ticket.save()
            
        return booking
    
    def validate_customer(self, value):
        if value:
            # Ensure customer belongs to the same company
            if value.company != self.context['request'].user.company:
                raise serializers.ValidationError("Customer does not belong to your company")
        return value
        
    def _generate_booking_reference(self):
        """Generate a unique booking reference."""
        # Format: 2 letters + 6 digits
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        digits = ''.join(random.choices(string.digits, k=6))
        booking_reference = f"{letters}{digits}"
        
        # Check if it already exists
        while Booking.objects.filter(booking_reference=booking_reference).exists():
            letters = ''.join(random.choices(string.ascii_uppercase, k=2))
            digits = ''.join(random.choices(string.digits, k=6))
            booking_reference = f"{letters}{digits}"
            
        return booking_reference


class ReceiptSerializer(serializers.ModelSerializer):
    """
    Serializer for Receipt model.
    """
    booking_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Receipt
        fields = '__all__'
        read_only_fields = ['id', 'company', 'receipt_number', 'created_at', 'updated_at']

    def get_booking_details(self, obj):
        return {
            'id': obj.booking.id,
            'booking_reference': obj.booking.booking_reference,
            'status': obj.booking.status,
            'final_amount': obj.booking.final_amount
        }

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        
        # Generate receipt number if not provided
        if 'receipt_number' not in validated_data:
            validated_data['receipt_number'] = self._generate_receipt_number()
            
        return super().create(validated_data)
        
    def validate_booking(self, value):
        # Ensure booking belongs to the same company
        if value.company != self.context['request'].user.company:
            raise serializers.ValidationError("Booking does not belong to your company")
        return value
        
    def validate_issued_by(self, value):
        if value:
            # Ensure employee belongs to the same company
            if value.company != self.context['request'].user.company:
                raise serializers.ValidationError("Employee does not belong to your company")
        return value
        
    def _generate_receipt_number(self):
        """Generate a unique receipt number."""
        # Format: R + 9 digits
        receipt_number = f"R{random.randint(100000000, 999999999)}"
        
        # Check if it already exists
        while Receipt.objects.filter(receipt_number=receipt_number).exists():
            receipt_number = f"R{random.randint(100000000, 999999999)}"
            
        return receipt_number


class DiscountSerializer(serializers.ModelSerializer):
    """
    Serializer for Discount model.
    """
    applicable_routes_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Discount
        fields = '__all__'
        read_only_fields = ['id', 'company', 'usage_count', 'created_at', 'updated_at']

    def get_applicable_routes_details(self, obj):
        return [{
            'id': route.id,
            'name': route.name,
            'origin': route.origin,
            'destination': route.destination
        } for route in obj.applicable_routes.all()]

    def create(self, validated_data):
        # Set company from request
        validated_data['company'] = self.context['request'].user.company
        return super().create(validated_data)
        
    def validate_applicable_routes(self, value):
        # Ensure all routes belong to the same company
        company = self.context['request'].user.company
        for route in value:
            if route.company != company:
                raise serializers.ValidationError(f"Route {route.name} does not belong to your company")
        return value
        
    def validate(self, data):
        # Validate date ranges
        if data.get('end_date') and data.get('start_date') and data.get('end_date') <= data.get('start_date'):
            raise serializers.ValidationError({'end_date': "End date must be after start date"})
            
        # Validate discount values
        if data.get('type') == 'Percentage' and data.get('value', 0) > 100:
            raise serializers.ValidationError({'value': "Percentage discount cannot exceed 100%"})
            
        return data


class TicketCheckInSerializer(serializers.Serializer):
    """
    Serializer for checking in a ticket.
    """
    checked_in_by = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), required=False
    )
    
    def validate_checked_in_by(self, value):
        if value:
            # Ensure user belongs to the same company
            if value.company != self.context['request'].user.company:
                raise serializers.ValidationError("User does not belong to your company")
        return value
