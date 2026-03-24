from rest_framework.exceptions import APIException
from rest_framework import status


class BusinessRuleViolation(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Regla de negocio violada.'


class ResourceNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Recurso no encontrado.'


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Conflicto con el estado actual del recurso.'
