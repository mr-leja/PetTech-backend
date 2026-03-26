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


class CalendarioVacunacion(models.Model):
    """Una por cada adopción confirmada. Generado automáticamente al aprobar."""
    adopcion = models.OneToOneField(
        Adopcion,
        on_delete=models.CASCADE,
        related_name='calendario',
    )
    notas = models.TextField(blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'calendarios_vacunacion'
        verbose_name = 'Calendario de Vacunación'
        verbose_name_plural = 'Calendarios de Vacunación'

    def __str__(self):
        return f'Calendario #{self.id} — {self.adopcion}'


class EntradaCalendario(models.Model):
    """Cada vacuna recomendada dentro de un CalendarioVacunacion."""
    calendario = models.ForeignKey(
        CalendarioVacunacion,
        on_delete=models.CASCADE,
        related_name='entradas',
    )
    nombre_vacuna = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    fecha_sugerida = models.DateField()
    es_refuerzo = models.BooleanField(default=False)
    completada = models.BooleanField(default=False)

    class Meta:
        db_table = 'entradas_calendario'
        verbose_name = 'Entrada de Calendario'
        verbose_name_plural = 'Entradas de Calendario'
        ordering = ['fecha_sugerida']

    def __str__(self):
        return f'{self.nombre_vacuna} — {self.fecha_sugerida}'
