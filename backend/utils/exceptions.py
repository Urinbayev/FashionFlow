"""
Custom exception handler for the FashionFlow API.
Provides consistent error response format across all endpoints.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns a consistent JSON format:
    {
        "error": true,
        "status_code": 400,
        "message": "Human-readable message",
        "errors": { ... }  // field-level errors if applicable
    }
    """
    # Convert Django ValidationError to DRF ValidationError
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            data = {
                "error": True,
                "status_code": 400,
                "message": "Validation error.",
                "errors": exc.message_dict,
            }
        else:
            data = {
                "error": True,
                "status_code": 400,
                "message": str(exc.message) if hasattr(exc, "message") else str(exc),
                "errors": {},
            }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    # Call default handler first
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code

        # Build a consistent error payload
        if isinstance(response.data, dict):
            # DRF returns a dict with field errors or {"detail": "..."}
            detail = response.data.pop("detail", None)
            errors = response.data if response.data else {}
            message = str(detail) if detail else "An error occurred."
        elif isinstance(response.data, list):
            message = " ".join(str(e) for e in response.data)
            errors = {}
        else:
            message = str(response.data)
            errors = {}

        response.data = {
            "error": True,
            "status_code": status_code,
            "message": message,
            "errors": errors,
        }

    return response


class BusinessLogicError(Exception):
    """Custom exception for business logic errors."""

    def __init__(self, message, code="business_error", status_code=400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)
