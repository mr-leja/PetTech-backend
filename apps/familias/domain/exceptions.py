from core.exceptions import BusinessRuleViolation, ResourceNotFound, ConflictError


class FamiliaYaRegistrada(ConflictError):
    default_detail = 'Ya tienes una familia registrada.'


class CondicionesHogarYaRegistradas(ConflictError):
    default_detail = 'Ya tienes condiciones de hogar registradas.'


class FamiliaNoEncontrada(ResourceNotFound):
    default_detail = 'Familia no encontrada.'


class AcuerdoResponsabilidadRequerido(BusinessRuleViolation):
    default_detail = 'Debes aceptar el acuerdo de responsabilidad para continuar.'
