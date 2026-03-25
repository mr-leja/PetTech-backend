from rest_framework import serializers
from apps.adopciones.infrastructure.models import SolicitudAdopcion, Adopcion


class SolicitudAdopcionSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(source='mascota.nombre', read_only=True)
    mascota_especie = serializers.CharField(source='mascota.especie', read_only=True)
    mascota_foto_url = serializers.SerializerMethodField()
    familia_nombre = serializers.CharField(source='familia.nombre_familia', read_only=True)
    familia_telefono = serializers.CharField(source='familia.telefono', read_only=True)
    familia_ciudad = serializers.CharField(source='familia.ciudad', read_only=True)
    familia_email = serializers.CharField(source='familia.usuario.email', read_only=True)
    condiciones_hogar = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudAdopcion
        fields = [
            'id',
            'mascota', 'mascota_nombre', 'mascota_especie', 'mascota_foto_url',
            'familia', 'familia_nombre', 'familia_telefono', 'familia_ciudad', 'familia_email',
            'condiciones_hogar',
            'estado', 'mensaje', 'notas_admin',
            'fecha_solicitud', 'fecha_decision',
        ]
        read_only_fields = [
            'id', 'estado', 'notas_admin', 'fecha_solicitud', 'fecha_decision',
            'mascota_nombre', 'mascota_especie', 'mascota_foto_url',
            'familia_nombre', 'familia_telefono', 'familia_ciudad', 'familia_email',
            'condiciones_hogar',
        ]

    def get_mascota_foto_url(self, obj):
        request = self.context.get('request')
        if obj.mascota.foto and request:
            return request.build_absolute_uri(obj.mascota.foto.url)
        return None

    def get_condiciones_hogar(self, obj):
        try:
            ch = obj.familia.condiciones_hogar
            return {
                'tipo_vivienda': ch.tipo_vivienda,
                'tiene_patio': ch.tiene_patio,
                'numero_personas': ch.numero_personas,
                'tiene_ninos': ch.tiene_ninos,
                'tamano_hogar': ch.tamano_hogar,
                'tiene_mascotas_actualmente': ch.tiene_mascotas_actualmente,
                'tiempo_solo_horas': ch.tiempo_solo_horas,
                'ingresos_estimados': ch.ingresos_estimados,
                'experiencia_mascotas': ch.experiencia_mascotas,
                'motivacion': ch.motivacion,
            }
        except Exception:
            return None


class SolicitudAdopcionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudAdopcion
        fields = ['mascota', 'mensaje']


class AdopcionSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(source='solicitud.mascota.nombre', read_only=True)
    mascota_especie = serializers.CharField(source='solicitud.mascota.especie', read_only=True)
    mascota_foto_url = serializers.SerializerMethodField()
    familia_nombre = serializers.CharField(source='solicitud.familia.nombre_familia', read_only=True)
    familia_email = serializers.CharField(source='solicitud.familia.usuario.email', read_only=True)

    class Meta:
        model = Adopcion
        fields = [
            'id', 'solicitud',
            'mascota_nombre', 'mascota_especie', 'mascota_foto_url',
            'familia_nombre', 'familia_email',
            'fecha_adopcion', 'notas',
        ]
        read_only_fields = ['id', 'fecha_adopcion']

    def get_mascota_foto_url(self, obj):
        request = self.context.get('request')
        if obj.solicitud.mascota.foto and request:
            return request.build_absolute_uri(obj.solicitud.mascota.foto.url)
        return None
