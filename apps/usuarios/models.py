# Re-exporta modelos desde infrastructure para que Django los descubra
from apps.usuarios.infrastructure.models import Usuario  # noqa: F401

__all__ = ['Usuario']
