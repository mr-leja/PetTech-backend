import uuid
from django.db import models
from django.conf import settings


class Mascota(models.Model):
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('EN_PROCESO', 'En proceso de adopción'),
        ('ADOPTADO', 'Adoptado'),
        ('NO_DISPONIBLE', 'No disponible'),
    ]
    ESPECIE_CHOICES = [
        ('PERRO', 'Perro'),
        ('GATO', 'Gato'),
        ('OTRO', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=10, choices=ESPECIE_CHOICES)
    raza = models.CharField(max_length=100, blank=True)
    edad_anios = models.PositiveSmallIntegerField(default=0)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='DISPONIBLE')
    foto = models.ImageField(upload_to='mascotas/', null=True, blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='mascotas_registradas',
    )
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mascotas'
        verbose_name = 'Mascota'
        verbose_name_plural = 'Mascotas'
        ordering = ['-fecha_ingreso']

    def __str__(self):
        return f'{self.nombre} ({self.especie}) - {self.estado}'
