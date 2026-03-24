from rest_framework import serializers
from apps.mascotas.infrastructure.models import Mascota


class MascotaSerializer(serializers.ModelSerializer):
    registrado_por_email = serializers.SerializerMethodField(read_only=True)
    foto_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Mascota
        fields = [
            'id', 'nombre', 'especie', 'raza', 'edad_anios',
            'descripcion', 'estado', 'foto', 'foto_url',
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
        fields = ['nombre', 'especie', 'raza', 'edad_anios', 'descripcion', 'estado', 'foto']

    def validate_edad_anios(self, value):
        if value < 0 or value > 30:
            raise serializers.ValidationError('La edad debe estar entre 0 y 30 años.')
        return value


class MascotaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'edad_anios', 'descripcion', 'estado', 'foto']
        extra_kwargs = {field: {'required': False} for field in fields}

    def validate_estado(self, value):
        instance = self.instance
        if instance and instance.estado == 'ADOPTADO' and value != 'ADOPTADO':
            raise serializers.ValidationError('No se puede cambiar el estado de una mascota adoptada.')
        return value
