"""
Models for the employees app, managing employee information.
"""
from django.db import models
from common.models import TenantModel


class EmployeeStatus(models.TextChoices):
    """Employee status enumeration"""
    ACTIVE = "Active"
    ON_LEAVE = "On Leave"
    INACTIVE = "Inactive"
    TERMINATED = "Terminated"


class EmployeeRole(models.TextChoices):
    """Employee role enumeration"""
    DRIVER = "Driver"
    CONDUCTOR = "Conductor"
    ADMIN = "Admin"
    MANAGER = "Manager"
    MECHANIC = "Mechanic"
    CUSTOMER_SERVICE = "Customer Service"
    OTHER = "Other"


class Employee(TenantModel):
    """
    Model representing an employee of the company.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=20,
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
            ("Prefer not to say", "Prefer not to say")
        ],
        blank=True,
        null=True
    )
    role = models.CharField(max_length=20, choices=EmployeeRole.choices)
    status = models.CharField(max_length=20, choices=EmployeeStatus.choices, default=EmployeeStatus.ACTIVE)
    department = models.CharField(max_length=100, blank=True, null=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='subordinates')
    hire_date = models.DateField()
    termination_date = models.DateField(blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bank_details = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    license_expiry_date = models.DateField(blank=True, null=True)
    license_type = models.CharField(max_length=50, blank=True, null=True)
    skills = models.JSONField(default=list)
    notes = models.TextField(blank=True, null=True)
    user = models.OneToOneField('accounts.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='employee')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        unique_together = ['company', 'email']


class Document(TenantModel):
    """
    Model representing an employee document.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=50,
        choices=[
            ("ID", "ID"),
            ("License", "License"),
            ("Passport", "Passport"),
            ("Certificate", "Certificate"),
            ("Contract", "Contract"),
            ("Other", "Other")
        ]
    )
    file_url = models.URLField()
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee} - {self.name} ({self.type})"

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"


class Leave(TenantModel):
    """
    Model representing an employee leave.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    type = models.CharField(
        max_length=50,
        choices=[
            ("Annual", "Annual"),
            ("Sick", "Sick"),
            ("Personal", "Personal"),
            ("Maternity", "Maternity"),
            ("Paternity", "Paternity"),
            ("Unpaid", "Unpaid"),
            ("Other", "Other")
        ]
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
            ("Cancelled", "Cancelled")
        ],
        default="Pending"
    )
    reason = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_leaves')
    approved_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee} - {self.type} ({self.start_date} to {self.end_date})"

    class Meta:
        verbose_name = "Leave"
        verbose_name_plural = "Leaves"


class Attendance(TenantModel):
    """
    Model representing an employee attendance record.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    clock_in = models.TimeField(blank=True, null=True)
    clock_out = models.TimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("Present", "Present"),
            ("Absent", "Absent"),
            ("Late", "Late"),
            ("Half Day", "Half Day"),
            ("On Leave", "On Leave")
        ],
        default="Present"
    )
    notes = models.TextField(blank=True, null=True)
    location_in = models.CharField(max_length=255, blank=True, null=True)
    location_out = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        unique_together = ['employee', 'date']
