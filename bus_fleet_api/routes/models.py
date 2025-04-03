"""
Models for the routes app, managing route and stop information.
"""
from django.db import models
from common.models import TenantModel


class RouteStatus(models.TextChoices):
    """Route status enumeration"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SEASONAL = "Seasonal"
    DISCONTINUED = "Discontinued"


class RouteType(models.TextChoices):
    """Route type enumeration"""
    EXPRESS = "Express"
    LOCAL = "Local"
    SHUTTLE = "Shuttle"
    CHARTER = "Charter"


class RouteFrequency(models.TextChoices):
    """Route frequency enumeration"""
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    BIWEEKLY = "Bi-Weekly"
    MONTHLY = "Monthly"
    CUSTOM = "Custom"


class Route(TenantModel):
    """
    Model representing a bus route.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    origin = models.CharField(max_length=100)
    origin_code = models.CharField(max_length=20)
    destination = models.CharField(max_length=100)
    destination_code = models.CharField(max_length=20)
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    distance_unit = models.CharField(max_length=5, choices=[("km", "km"), ("miles", "miles")], default="km")
    duration = models.IntegerField()  # in minutes
    duration_unit = models.CharField(
        max_length=10, 
        choices=[("minutes", "minutes"), ("hours", "hours")], 
        default="minutes"
    )
    status = models.CharField(max_length=20, choices=RouteStatus.choices, default=RouteStatus.ACTIVE)
    type = models.CharField(max_length=20, choices=RouteType.choices, default=RouteType.EXPRESS)
    frequency = models.CharField(max_length=20, choices=RouteFrequency.choices, default=RouteFrequency.DAILY)
    first_departure = models.TimeField(blank=True, null=True)
    last_departure = models.TimeField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name} ({self.origin} to {self.destination})"

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        unique_together = ['company', 'code']


class RouteStop(TenantModel):
    """
    Model representing a stop along a bus route.
    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    arrival_time = models.TimeField(blank=True, null=True)
    departure_time = models.TimeField(blank=True, null=True)
    wait_time = models.IntegerField(blank=True, null=True)  # in minutes
    stop_number = models.PositiveIntegerField()
    is_origin = models.BooleanField(default=False)
    is_destination = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.route.code} - Stop {self.stop_number}: {self.name}"

    class Meta:
        verbose_name = "Route Stop"
        verbose_name_plural = "Route Stops"
        ordering = ['route', 'stop_number']
        unique_together = ['route', 'stop_number']


class RouteSchedule(TenantModel):
    """
    Model representing a schedule for a bus route.
    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    days_of_week = models.JSONField(help_text="Array of weekday numbers (0-6, 0 is Monday)")
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.route.code} - {self.departure_time} to {self.arrival_time}"

    class Meta:
        verbose_name = "Route Schedule"
        verbose_name_plural = "Route Schedules"
