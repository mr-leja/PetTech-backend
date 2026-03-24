from django.contrib import admin
from apps.familias.infrastructure.models import Familia, CondicionesHogar


@admin.register(Familia)
class FamiliaAdmin(admin.ModelAdmin):
    list_display = ['nombre_familia', 'usuario', 'ciudad', 'departamento', 'fecha_registro']
    search_fields = ['nombre_familia', 'usuario__email']
    ordering = ['-fecha_registro']


@admin.register(CondicionesHogar)
class CondicionesHogarAdmin(admin.ModelAdmin):
    list_display = ['familia', 'tipo_vivienda', 'numero_personas', 'acuerdo_responsabilidad']
    list_filter = ['tipo_vivienda', 'acuerdo_responsabilidad']
