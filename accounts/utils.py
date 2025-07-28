from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils.translation import gettext_lazy as _


def custom_exception_handler(exc, context):
    """
    Custom exception handler for better error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the error response format
        if isinstance(response.data, dict):
            response.data = {
                'error': True,
                'message': response.data.get('detail', 'An error occurred'),
                'data': None
            }
        elif isinstance(response.data, list):
            response.data = {
                'error': True,
                'message': 'Validation error',
                'data': response.data
            }
    
    # Handle Django's ValidationError
    elif isinstance(exc, ValidationError):
        response = Response({
            'error': True,
            'message': 'Validation error',
            'data': exc.messages
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle Django's Http404
    elif isinstance(exc, Http404):
        response = Response({
            'error': True,
            'message': 'Not found',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)
    
    return response 