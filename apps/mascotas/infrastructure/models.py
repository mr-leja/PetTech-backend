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
        ('CONEJO', 'Conejo'),
        ('HAMSTER', 'Hámster'),
    ]
    TAMANO_CHOICES = [
        ('PEQUENO', 'Pequeño'),
        ('MEDIANO', 'Mediano'),
        ('GRANDE', 'Grande'),
    ]
    SEXO_CHOICES = [
        ('MACHO', 'Macho'),
        ('HEMBRA', 'Hembra'),
    ]
    ENERGIA_CHOICES = [
        ('BAJO', 'Bajo'),
        ('MEDIO', 'Medio'),
        ('ALTO', 'Alto'),
    ]
    EDAD_UNIDAD_CHOICES = [
        ('ANIOS', 'Años'),
        ('MESES', 'Meses'),
    ]

    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=10, choices=ESPECIE_CHOICES)
    raza = models.CharField(max_length=100, blank=True)
    edad_anios = models.PositiveSmallIntegerField(default=0)
    edad_unidad = models.CharField(max_length=6, choices=EDAD_UNIDAD_CHOICES, default='ANIOS')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    tamano = models.CharField(max_length=10, choices=TAMANO_CHOICES, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sexo = models.CharField(max_length=6, choices=SEXO_CHOICES, blank=True)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='DISPONIBLE')
    foto = models.ImageField(upload_to='mascotas/', null=True, blank=True)
    nivel_energia = models.CharField(max_length=6, choices=ENERGIA_CHOICES, blank=True)
    historial_vacunas = models.JSONField(default=list, blank=True)
    carnet_vacunas = models.FileField(upload_to='carnets/', null=True, blank=True)
    historia_mascota = models.TextField(blank=True)
    info_adicional = models.TextField(blank=True)
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
