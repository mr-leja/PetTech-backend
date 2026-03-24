from core.exceptions import BusinessRuleViolation, ResourceNotFound


class MascotaYaAdoptada(BusinessRuleViolation):
    default_detail = 'Esta mascota ya fue adoptada y no puede modificarse.'


class MascotaNoEncontrada(ResourceNotFound):
    default_detail = 'Mascota no encontrada.'
