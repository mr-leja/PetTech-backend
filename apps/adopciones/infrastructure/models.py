from django.db import models
from apps.mascotas.infrastructure.models import Mascota
from apps.familias.infrastructure.models import Familia


class SolicitudAdopcion(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.PROTECT,
        related_name='solicitudes',
    )
    familia = models.ForeignKey(
        Familia,
        on_delete=models.PROTECT,
        related_name='solicitudes',
    )
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')
    mensaje = models.TextField(blank=True, help_text='Mensaje opcional de la familia al administrador.')
    notas_admin = models.TextField(blank=True, help_text='Notas del administrador sobre la decisión.')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_decision = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'solicitudes_adopcion'
        verbose_name = 'Solicitud de Adopción'
        verbose_name_plural = 'Solicitudes de Adopción'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f'Solicitud #{self.id} — {self.familia.nombre_familia} → {self.mascota.nombre} ({self.estado})'


class Adopcion(models.Model):
    solicitud = models.OneToOneField(
        SolicitudAdopcion,
        on_delete=models.PROTECT,
        related_name='adopcion',
    )
    fecha_adopcion = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True)

    class Meta:
        db_table = 'adopciones'
        verbose_name = 'Adopción'
        verbose_name_plural = 'Adopciones'
        ordering = ['-fecha_adopcion']

    def __str__(self):
        return f'Adopción #{self.id} — {self.solicitud.familia.nombre_familia} adoptó a {self.solicitud.mascota.nombre}'
