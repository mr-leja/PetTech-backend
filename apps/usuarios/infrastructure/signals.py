import logging
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    """Crea el admin por defecto al ejecutar migraciones si no existe."""
    if sender.name != 'apps.usuarios':
        return
    try:
        from apps.usuarios.infrastructure.models import Usuario
        email = getattr(settings, 'DEFAULT_ADMIN_EMAIL', 'admin@pettech.com')
        password = getattr(settings, 'DEFAULT_ADMIN_PASSWORD', 'Admin1234!')
        if not Usuario.objects.filter(email=email).exists():
            Usuario.objects.create_superuser(
                email=email,
                password=password,
                nombre='Administrador PetTech',
                rol='ADMIN',
            )
            logger.info('Admin por defecto creado: %s', email)
    except Exception as e:
        logger.warning('No se pudo crear admin por defecto: %s', e)
