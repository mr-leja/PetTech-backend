from django.contrib import admin
from apps.mascotas.infrastructure.models import Mascota


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'especie', 'raza', 'edad_anios', 'estado', 'registrado_por', 'fecha_ingreso']
    list_filter = ['estado', 'especie']
    search_fields = ['nombre', 'raza']
    ordering = ['-fecha_ingreso']
