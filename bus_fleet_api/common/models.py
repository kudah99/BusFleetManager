"""
Common models and base classes for the bus fleet management API.
"""
from django.db import models
import uuid


class BaseModel(models.Model):
    """
    Base model with common fields for all models in the system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantModel(BaseModel):
    """
    Base model for all tenant-specific models.
    Includes a reference to the company.
    """
    company = models.ForeignKey(
        'accounts.Company', 
        on_delete=models.CASCADE,
        related_name="%(class)ss"
    )

    class Meta:
        abstract = True
