from core.exceptions import ResourceNotFound, ConflictError, BusinessRuleViolation


class SolicitudNoEncontrada(ResourceNotFound):
    default_detail = 'Solicitud de adopción no encontrada.'


class MascotaNoDisponible(ConflictError):
    default_detail = 'La mascota no está disponible para adopción.'


class SolicitudYaDecidida(ConflictError):
    default_detail = 'La solicitud ya tiene una decisión final y no puede modificarse.'


class FamiliaRequerida(BusinessRuleViolation):
    default_detail = 'Debes registrar tu perfil de familia antes de solicitar una adopción.'
