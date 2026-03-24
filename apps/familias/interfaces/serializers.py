from rest_framework import serializers
from apps.familias.infrastructure.models import Familia, CondicionesHogar


class CondicionesHogarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CondicionesHogar
        fields = [
            'id', 'tipo_vivienda', 'propiedad_vivienda', 'tiene_patio',
            'numero_personas', 'tiene_ninos', 'tamano_hogar',
            'tiene_mascotas_actualmente', 'otras_mascotas',
            'tiempo_solo_horas', 'ingresos_estimados',
            'experiencia_mascotas', 'motivacion',
            'acuerdo_responsabilidad', 'fecha_registro',
        ]
        read_only_fields = ['id', 'fecha_registro']

    def validate_acuerdo_responsabilidad(self, value):
        if not value:
            raise serializers.ValidationError('Debes aceptar el acuerdo de responsabilidad.')
        return value


class FamiliaSerializer(serializers.ModelSerializer):
    condiciones_hogar = CondicionesHogarSerializer(read_only=True)
    usuario_email = serializers.SerializerMethodField()
    foto_cedula_url = serializers.SerializerMethodField()

    class Meta:
        model = Familia
        fields = [
            'id', 'usuario', 'usuario_email', 'nombre_familia',
            'cedula', 'foto_cedula_url', 'edad',
            'telefono', 'ciudad', 'departamento', 'direccion',
            'redes_sociales',
            'condiciones_hogar', 'fecha_registro',
        ]
        read_only_fields = ['id', 'usuario', 'fecha_registro']

    def get_usuario_email(self, obj):
        return obj.usuario.email

    def get_foto_cedula_url(self, obj):
        if obj.foto_cedula:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.foto_cedula.url)
            return obj.foto_cedula.url
        return None


class FamiliaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Familia
        fields = [
            'nombre_familia', 'cedula', 'foto_cedula', 'edad',
            'telefono', 'ciudad', 'departamento', 'direccion', 'redes_sociales',
        ]

    def validate_telefono(self, value):
        cleaned = ''.join(c for c in value if c.isdigit() or c in ('+', '-', ' '))
        if len(cleaned) < 7:
            raise serializers.ValidationError('El teléfono debe tener al menos 7 dígitos.')
        return cleaned

    def validate_edad(self, value):
        if value is not None and value < 18:
            raise serializers.ValidationError('Debes ser mayor de edad (18 años o más).')
        return value
