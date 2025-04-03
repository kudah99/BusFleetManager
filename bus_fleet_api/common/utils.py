"""
Utility functions for the bus fleet management system.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError


def custom_exception_handler(exc, context):
    """
    Custom exception handler for the API.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # If response is not None, it's already handled
    if response is not None:
        return response

    # Handle database integrity errors
    if isinstance(exc, IntegrityError):
        return Response(
            {"detail": "Database integrity error. This could be due to a duplicate record or invalid foreign key."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Handle any other unhandled exceptions
    return Response(
        {"detail": "An unexpected error occurred."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def generate_report_data(model_objects, field_names, additional_data=None):
    """
    Generate report data from model objects.
    
    Args:
        model_objects: QuerySet of model objects
        field_names: List of field names to include in the report
        additional_data: Dict of additional data to include in the report
        
    Returns:
        Dict containing report data
    """
    data = {
        'count': model_objects.count(),
        'results': [],
        'additional_data': additional_data or {}
    }
    
    for obj in model_objects:
        item = {}
        for field in field_names:
            if hasattr(obj, field):
                item[field] = getattr(obj, field)
        data['results'].append(item)
        
    return data
