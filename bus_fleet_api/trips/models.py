"""
Models for the trips app, managing trip information.
"""
from django.db import models
from common.models import TenantModel
from django.utils import timezone


class TripStatus(models.TextChoices):
    """Trip status enumeration"""
    SCHEDULED = "Scheduled"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    DELAYED = "Delayed"


class Trip(TenantModel):
    """
    Model representing a bus trip.
    """
    route = models.ForeignKey('routes.Route', on_delete=models.CASCADE, related_name='trips')
    bus = models.ForeignKey('buses.Bus', on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='driver_trips')
    conductor = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL, 
        related_name='conductor_trips', blank=True, null=True
    )
    departure_date = models.DateField()
    departure_time = models.TimeField()
    arrival_date = models.DateField()
    arrival_time = models.TimeField()
    status = models.CharField(max_length=20, choices=TripStatus.choices, default=TripStatus.SCHEDULED)
    capacity = models.PositiveIntegerField()
    booked_seats = models.PositiveIntegerField(default=0)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    actual_departure = models.DateTimeField(blank=True, null=True)
    actual_arrival = models.DateTimeField(blank=True, null=True)
    delay_reason = models.TextField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.route.name} - {self.departure_date} {self.departure_time}"

    class Meta:
        verbose_name = "Trip"
        verbose_name_plural = "Trips"
        ordering = ['-departure_date', '-departure_time']


class TripEvent(TenantModel):
    """
    Model representing an event that occurs during a trip.
    """
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(
        max_length=50,
        choices=[
            ("Departure", "Departure"),
            ("Arrival", "Arrival"),
            ("Stop", "Stop"),
            ("Delay", "Delay"),
            ("Breakdown", "Breakdown"),
            ("Accident", "Accident"),
            ("Weather", "Weather"),
            ("Other", "Other")
        ]
    )
    timestamp = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    recorded_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL, 
        related_name='recorded_events', blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)
    duration = models.PositiveIntegerField(blank=True, null=True, help_text="Duration in minutes")

    def __str__(self):
        return f"{self.trip} - {self.event_type} at {self.timestamp}"

    class Meta:
        verbose_name = "Trip Event"
        verbose_name_plural = "Trip Events"
        ordering = ['-timestamp']


class TripStop(TenantModel):
    """
    Model representing a stop during a specific trip.
    """
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='trip_stops')
    route_stop = models.ForeignKey('routes.RouteStop', on_delete=models.CASCADE, related_name='trip_stops')
    scheduled_arrival = models.DateTimeField()
    scheduled_departure = models.DateTimeField()
    actual_arrival = models.DateTimeField(blank=True, null=True)
    actual_departure = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Arrived", "Arrived"),
            ("Departed", "Departed"),
            ("Skipped", "Skipped"),
            ("Cancelled", "Cancelled")
        ],
        default="Pending"
    )
    passengers_boarding = models.PositiveIntegerField(default=0)
    passengers_alighting = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.trip} - Stop at {self.route_stop.name}"

    class Meta:
        verbose_name = "Trip Stop"
        verbose_name_plural = "Trip Stops"
        ordering = ['scheduled_arrival']
        unique_together = ['trip', 'route_stop']
