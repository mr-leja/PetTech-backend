import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, DjangoValidationError):
        response = Response(
            {'error': exc.messages},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if response is not None:
        error_data = {
            'error': response.data,
            'status_code': response.status_code,
        }
        if isinstance(response.data, dict) and 'detail' in response.data:
            error_data['error'] = str(response.data['detail'])
        elif isinstance(response.data, list):
            error_data['error'] = response.data
        response.data = error_data

    return response
