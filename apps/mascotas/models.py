# Re-exporta modelos desde infrastructure para que Django los descubra
from apps.mascotas.infrastructure.models import Mascota  # noqa: F401

__all__ = ['Mascota']
