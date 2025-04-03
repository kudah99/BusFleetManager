"""
Models for the buses app, managing bus fleet information.
"""
from django.db import models
from common.models import TenantModel
from employees.models import Employee


class BusStatus(models.TextChoices):
    """Bus status enumeration"""
    ACTIVE = "Active"
    MAINTENANCE = "Maintenance"
    INACTIVE = "Inactive"
    RETIRED = "Retired"


class BusType(models.TextChoices):
    """Bus type enumeration"""
    STANDARD = "Standard"
    LUXURY = "Luxury"
    MINIBUS = "Minibus"
    DOUBLE_DECKER = "Double Decker"
    SLEEPER = "Sleeper"


class FuelType(models.TextChoices):
    """Fuel type enumeration"""
    DIESEL = "Diesel"
    GASOLINE = "Gasoline"
    ELECTRIC = "Electric"
    HYBRID = "Hybrid"
    CNG = "CNG"
    LNG = "LNG"


class Location(TenantModel):
    """
    Model representing a location for buses.
    """
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_terminal = models.BooleanField(default=False)
    is_maintenance_facility = models.BooleanField(default=False)
    is_office = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.city}, {self.country})"

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"


class Bus(TenantModel):
    """
    Model representing a bus in the fleet.
    """
    registration_number = models.CharField(max_length=50)
    license_plate = models.CharField(max_length=20)
    model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    type = models.CharField(max_length=20, choices=BusType.choices, default=BusType.STANDARD)
    capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=BusStatus.choices, default=BusStatus.ACTIVE)
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices, default=FuelType.DIESEL)
    mileage = models.PositiveIntegerField(default=0)
    last_maintenance_date = models.DateField(blank=True, null=True)
    next_maintenance_date = models.DateField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    insurance_expiry_date = models.DateField(blank=True, null=True)
    current_location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, 
        blank=True, null=True, related_name='buses'
    )
    assigned_driver = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, 
        blank=True, null=True, related_name='assigned_buses'
    )
    features = models.JSONField(default=list)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.registration_number} - {self.model} ({self.year})"

    class Meta:
        verbose_name = "Bus"
        verbose_name_plural = "Buses"
        unique_together = ['company', 'registration_number']


class BusMaintenance(TenantModel):
    """
    Model representing a maintenance record for a bus.
    """
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='maintenance_records')
    date = models.DateField()
    type = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    mileage = models.PositiveIntegerField()
    technician_id = models.CharField(max_length=50, blank=True, null=True)
    technician_name = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    parts = models.JSONField(default=list)
    status = models.CharField(
        max_length=20,
        choices=[
            ("Scheduled", "Scheduled"),
            ("In Progress", "In Progress"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled")
        ],
        default="Scheduled"
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.bus.registration_number} - {self.type} ({self.date})"

    class Meta:
        verbose_name = "Bus Maintenance"
        verbose_name_plural = "Bus Maintenances"


class BusExpense(TenantModel):
    """
    Model representing an expense record for a bus.
    """
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    type = models.CharField(
        max_length=20,
        choices=[
            ("Fuel", "Fuel"),
            ("Maintenance", "Maintenance"),
            ("Insurance", "Insurance"),
            ("Registration", "Registration"),
            ("Toll", "Toll"),
            ("Parking", "Parking"),
            ("Cleaning", "Cleaning"),
            ("Other", "Other")
        ]
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    receipt_url = models.URLField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.bus.registration_number} - {self.type} ({self.date})"

    class Meta:
        verbose_name = "Bus Expense"
        verbose_name_plural = "Bus Expenses"


class BusDocument(TenantModel):
    """
    Model representing a document associated with a bus.
    """
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='documents')
    type = models.CharField(
        max_length=20,
        choices=[
            ("Registration", "Registration"),
            ("Insurance", "Insurance"),
            ("Inspection", "Inspection"),
            ("Permit", "Permit"),
            ("Warranty", "Warranty"),
            ("Purchase", "Purchase"),
            ("Other", "Other")
        ]
    )
    name = models.CharField(max_length=100)
    file_url = models.URLField(blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.bus.registration_number} - {self.type} ({self.name})"

    class Meta:
        verbose_name = "Bus Document"
        verbose_name_plural = "Bus Documents"
