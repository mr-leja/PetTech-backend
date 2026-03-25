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
    foto_perfil_url = serializers.SerializerMethodField()

    class Meta:
        model = Familia
        fields = [
            'id', 'usuario', 'usuario_email', 'nombre_familia',
            'cedula', 'fecha_nacimiento',
            'telefono', 'ciudad', 'departamento', 'direccion',
            'redes_sociales', 'foto_perfil', 'foto_perfil_url',
            'condiciones_hogar', 'fecha_registro',
        ]
        read_only_fields = ['id', 'usuario', 'fecha_registro']

    def get_foto_perfil_url(self, obj):
        request = self.context.get('request')
        if obj.foto_perfil and request:
            return request.build_absolute_uri(obj.foto_perfil.url)
        return None

    def get_usuario_email(self, obj):
        return obj.usuario.email


class FamiliaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Familia
        fields = [
            'nombre_familia', 'cedula', 'fecha_nacimiento',
            'telefono', 'ciudad', 'departamento', 'direccion',
            'redes_sociales', 'foto_perfil',
        ]

    def validate_foto_perfil(self, value):
        if value is None:
            return value
        allowed_types = ('image/jpeg', 'image/png', 'image/webp')
        if value.content_type not in allowed_types:
            raise serializers.ValidationError('Solo se permiten imágenes JPEG, PNG o WebP.')
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('La imagen no puede superar 5 MB.')
        return value

    def validate_telefono(self, value):
        cleaned = ''.join(c for c in value if c.isdigit() or c in ('+', '-', ' '))
        if len(cleaned) < 7:
            raise serializers.ValidationError('El teléfono debe tener al menos 7 dígitos.')
        return cleaned

    def validate_fecha_nacimiento(self, value):
        from datetime import date
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError('Debes ser mayor de edad (18 años o más).')
        return value
