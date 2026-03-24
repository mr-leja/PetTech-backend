from rest_framework import serializers
from apps.mascotas.infrastructure.models import Mascota

_WRITE_FIELDS = [
    'nombre', 'especie', 'raza', 'edad_anios', 'edad_unidad',
    'fecha_nacimiento', 'tamano', 'peso', 'sexo',
    'descripcion', 'estado', 'foto',
    'nivel_energia', 'historial_vacunas', 'historia_mascota', 'info_adicional',
]


class MascotaSerializer(serializers.ModelSerializer):
    registrado_por_email = serializers.SerializerMethodField(read_only=True)
    foto_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Mascota
        fields = [
            'id', 'nombre', 'especie', 'raza', 'edad_anios', 'edad_unidad',
            'fecha_nacimiento', 'tamano', 'peso', 'sexo',
            'descripcion', 'estado', 'foto', 'foto_url',
            'nivel_energia', 'historial_vacunas', 'historia_mascota', 'info_adicional',
            'registrado_por', 'registrado_por_email',
            'fecha_ingreso', 'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'registrado_por', 'fecha_ingreso', 'fecha_actualizacion']
        extra_kwargs = {'foto': {'write_only': True, 'required': False}}

    def get_registrado_por_email(self, obj):
        return obj.registrado_por.email if obj.registrado_por else None

    def get_foto_url(self, obj):
        request = self.context.get('request')
        if obj.foto and request:
            return request.build_absolute_uri(obj.foto.url)
        return None


class MascotaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = _WRITE_FIELDS

    def validate_edad_anios(self, value):
        if value < 0 or value > 99:
            raise serializers.ValidationError('La edad debe estar entre 0 y 99.')
        return value


class MascotaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = _WRITE_FIELDS
        extra_kwargs = {field: {'required': False} for field in _WRITE_FIELDS}

    def validate_estado(self, value):
        instance = self.instance
        if instance and instance.estado == 'ADOPTADO' and value != 'ADOPTADO':
            raise serializers.ValidationError('No se puede cambiar el estado de una mascota adoptada.')
        return value
