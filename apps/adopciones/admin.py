from django.contrib import admin
from apps.adopciones.infrastructure.models import SolicitudAdopcion, Adopcion


@admin.register(SolicitudAdopcion)
class SolicitudAdopcionAdmin(admin.ModelAdmin):
    list_display = ['id', 'mascota', 'familia', 'estado', 'fecha_solicitud', 'fecha_decision']
    list_filter = ['estado']
    search_fields = ['mascota__nombre', 'familia__nombre_familia']
    readonly_fields = ['fecha_solicitud', 'fecha_decision']


@admin.register(Adopcion)
class AdopcionAdmin(admin.ModelAdmin):
    list_display = ['id', 'solicitud', 'fecha_adopcion']
    readonly_fields = ['fecha_adopcion']
