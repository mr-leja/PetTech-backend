# Re-exporta modelos desde infrastructure para que Django los descubra
from apps.familias.infrastructure.models import Familia, CondicionesHogar  # noqa: F401

__all__ = ['Familia', 'CondicionesHogar']
