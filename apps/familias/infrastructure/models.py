from django.db import models
from django.conf import settings


class Familia(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='familia',
    )
    nombre_familia = models.CharField(max_length=200)
    cedula = models.CharField(max_length=20, default='')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    direccion = models.CharField(max_length=300, default='')
    redes_sociales = models.CharField(max_length=200, blank=True)
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
    PROPIEDAD_CHOICES = [
        ('PROPIA', 'Propia'),
        ('ALQUILADA', 'Alquilada'),
    ]
    TAMANO_HOGAR_CHOICES = [
        ('PEQUENO', 'Pequeño (< 50 m²)'),
        ('MEDIANO', 'Mediano (50–120 m²)'),
        ('GRANDE', 'Grande (> 120 m²)'),
    ]
    INGRESOS_CHOICES = [
        ('MENOS_1SMLV', 'Menos de 1 SMLV'),
        ('1_2SMLV', '1–2 SMLV'),
        ('2_4SMLV', '2–4 SMLV'),
        ('MAS_4SMLV', 'Más de 4 SMLV'),
    ]

    familia = models.OneToOneField(
        Familia,
        on_delete=models.CASCADE,
        related_name='condiciones_hogar',
    )
    tipo_vivienda = models.CharField(max_length=15, choices=TIPO_VIVIENDA_CHOICES)
    propiedad_vivienda = models.CharField(max_length=15, choices=PROPIEDAD_CHOICES, default='PROPIA')
    tiene_patio = models.BooleanField(default=False)
    numero_personas = models.PositiveSmallIntegerField()
    tiene_ninos = models.BooleanField(default=False)
    tamano_hogar = models.CharField(max_length=10, choices=TAMANO_HOGAR_CHOICES, default='MEDIANO')
    tiene_mascotas_actualmente = models.BooleanField(default=False)
    otras_mascotas = models.JSONField(default=list)
    tiempo_solo_horas = models.PositiveSmallIntegerField(default=0)
    ingresos_estimados = models.CharField(max_length=30, choices=INGRESOS_CHOICES, blank=True)
    experiencia_mascotas = models.TextField(blank=True)
    motivacion = models.TextField(blank=True)
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
