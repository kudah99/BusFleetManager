"""
Models for the tickets app, managing ticket bookings and payments.
"""
from django.db import models
from common.models import TenantModel
from django.utils import timezone


class TicketStatus(models.TextChoices):
    """Ticket status enumeration"""
    RESERVED = "Reserved"
    CONFIRMED = "Confirmed"
    CHECKED_IN = "Checked In"
    USED = "Used"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"
    EXPIRED = "Expired"


class TicketType(models.TextChoices):
    """Ticket type enumeration"""
    ONE_WAY = "One Way"
    ROUND_TRIP = "Round Trip"
    MULTI_CITY = "Multi City"
    SUBSCRIPTION = "Subscription"
    SPECIAL = "Special"


class PaymentStatus(models.TextChoices):
    """Payment status enumeration"""
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"
    PARTIALLY_REFUNDED = "Partially Refunded"


class PaymentMethod(models.TextChoices):
    """Payment method enumeration"""
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    PAYPAL = "PayPal"
    BANK_TRANSFER = "Bank Transfer"
    CASH = "Cash"
    MOBILE_PAYMENT = "Mobile Payment"
    OTHER = "Other"


class Ticket(TenantModel):
    """
    Model representing a bus ticket.
    """
    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE, related_name='tickets')
    customer = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='tickets'
    )
    booking_reference = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=20, 
        choices=TicketStatus.choices, 
        default=TicketStatus.RESERVED
    )
    type = models.CharField(
        max_length=20, 
        choices=TicketType.choices, 
        default=TicketType.ONE_WAY
    )
    seat_number = models.CharField(max_length=10, blank=True, null=True)
    passenger_name = models.CharField(max_length=100)
    passenger_email = models.EmailField(blank=True, null=True)
    passenger_phone = models.CharField(max_length=20, blank=True, null=True)
    passenger_type = models.CharField(
        max_length=20,
        choices=[
            ("Adult", "Adult"),
            ("Child", "Child"),
            ("Senior", "Senior"),
            ("Student", "Student"),
            ("Military", "Military"),
            ("Other", "Other")
        ],
        default="Adult"
    )
    special_requests = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices, 
        blank=True, null=True
    )
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    checked_in_at = models.DateTimeField(blank=True, null=True)
    checked_in_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL, 
        blank=True, null=True, related_name='checked_in_tickets'
    )
    cancellation_reason = models.TextField(blank=True, null=True)
    cancellation_date = models.DateTimeField(blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    refund_date = models.DateTimeField(blank=True, null=True)
    refund_reference = models.CharField(max_length=100, blank=True, null=True)
    issued_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.booking_reference} - {self.passenger_name} ({self.trip})"

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-issued_at']


class BookingStatus(models.TextChoices):
    """Booking status enumeration"""
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class BookingSource(models.TextChoices):
    """Booking source enumeration"""
    WEBSITE = "Website"
    MOBILE_APP = "Mobile App"
    PHONE = "Phone"
    IN_PERSON = "In Person"
    WHATSAPP = "WhatsApp"
    AGENT = "Agent"
    OTHER = "Other"


class Booking(TenantModel):
    """
    Model representing a booking, which can contain multiple tickets.
    """
    customer = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='bookings'
    )
    booking_reference = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices, 
        blank=True, null=True
    )
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    source = models.CharField(
        max_length=20,
        choices=BookingSource.choices,
        default=BookingSource.WEBSITE
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.booking_reference} - {self.final_amount}"

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['-created_at']


class ReceiptType(models.TextChoices):
    """Receipt type enumeration"""
    DIGITAL = "Digital"
    PRINTED = "Printed"
    BOTH = "Both"


class DiscountType(models.TextChoices):
    """Discount type enumeration"""
    PERCENTAGE = "Percentage"
    FIXED_AMOUNT = "Fixed Amount"


class Receipt(TenantModel):
    """
    Model representing a receipt for a booking.
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='receipts')
    receipt_number = models.CharField(max_length=20, unique=True)
    type = models.CharField(
        max_length=10,
        choices=ReceiptType.choices,
        default=ReceiptType.DIGITAL
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    issued_at = models.DateTimeField(default=timezone.now)
    issued_by = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL, 
        blank=True, null=True, related_name='issued_receipts'
    )
    sent_to = models.EmailField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    printed_at = models.DateTimeField(blank=True, null=True)
    digital_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.receipt_number} - {self.booking.booking_reference}"

    class Meta:
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"
        ordering = ['-issued_at']


class Discount(TenantModel):
    """
    Model representing a discount code.
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE
    )
    value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    usage_limit = models.PositiveIntegerField(blank=True, null=True)
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    applicable_routes = models.ManyToManyField('routes.Route', blank=True, related_name='discounts')
    applicable_trip_types = models.JSONField(default=list)
    applicable_user_groups = models.JSONField(default=list)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"
        ordering = ['-created_at']
