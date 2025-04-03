#!/usr/bin/env python
"""
Main entry point for the bus fleet management API.
"""
import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Django
django.setup()

# Import necessary modules
from django.core.management import execute_from_command_line
import uvicorn

def run_server():
    """Run the Django development server with Uvicorn."""
    print("Starting Bus Fleet Management API on http://0.0.0.0:8000")
    print("API Documentation available at http://0.0.0.0:8000/api/")
    uvicorn.run(
        "core.asgi:application",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

def run_django_command(command):
    """Run a Django management command."""
    execute_from_command_line([sys.argv[0]] + command.split())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "runserver":
            run_server()
        else:
            # Run the Django management command
            execute_from_command_line(sys.argv)
    else:
        # Default to running the server
        run_server()
