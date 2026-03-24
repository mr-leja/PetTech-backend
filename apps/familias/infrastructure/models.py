from django.db import models
from django.conf import settings


class Familia(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='familia',
    )
    nombre_familia = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'familias'
        verbose_name = 'Familia'
        verbose_name_plural = 'Familias'

    def __str__(self):
        return f'{self.nombre_familia} (usuario: {self.usuario.email})'


class CondicionesHogar(models.Model):
    TIPO_VIVIENDA_CHOICES = [
        ('CASA', 'Casa'),
        ('APARTAMENTO', 'Apartamento'),
        ('FINCA', 'Finca'),
        ('OTRO', 'Otro'),
    ]

    familia = models.OneToOneField(
        Familia,
        on_delete=models.CASCADE,
        related_name='condiciones_hogar',
    )
    tipo_vivienda = models.CharField(max_length=15, choices=TIPO_VIVIENDA_CHOICES)
    tiene_patio = models.BooleanField(default=False)
    numero_personas = models.PositiveSmallIntegerField()
    tiene_mascotas_actualmente = models.BooleanField(default=False)
    experiencia_mascotas = models.TextField(blank=True)
    acuerdo_responsabilidad = models.BooleanField(
        default=False,
        help_text='Usuario aceptó el acuerdo de responsabilidad (HU-05)'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'condiciones_hogar'
        verbose_name = 'Condiciones del Hogar'
        verbose_name_plural = 'Condiciones del Hogar'

    def __str__(self):
        return f'Hogar de {self.familia.nombre_familia}'
