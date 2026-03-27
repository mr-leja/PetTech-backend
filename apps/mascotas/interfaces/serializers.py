import re
from rest_framework import serializers
from django.conf import settings
from apps.mascotas.infrastructure.models import Mascota


def _cloudinary_url(name: str, resource_type: str = 'image') -> str | None:
    """
    Construye una URL válida de Cloudinary a partir del nombre guardado en la BD.

    django-cloudinary-storage 0.3.x almacena el valor de retorno de _save() como
    nombre del campo. En algunas configuraciones guarda la URL completa con una
    sola barra (https:/res.cloudinary.com/...) en lugar del public_id puro.  Este
    helper extrae el public_id real en ambos casos.
    """
    if not name:
        return None
    cloud = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', '')
    # Caso: nombre guardado como URL de Cloudinary (posiblemente con https:/ simple)
    match = re.search(r'cloudinary\.com/([^/]+)/(.+)$', name)
    if match:
        cloud = match.group(1)
        path = match.group(2)
        # Quitar prefijo de resource_type si ya está presente (image/upload/, raw/upload/…)
        path = re.sub(r'^(?:image|raw|video)/upload/(?:v\d+/)?', '', path)
        return f'https://res.cloudinary.com/{cloud}/{resource_type}/upload/{path}'
    # Caso: nombre es directamente el public_id
    return f'https://res.cloudinary.com/{cloud}/{resource_type}/upload/{name}'


_WRITE_FIELDS = [
    'nombre', 'especie', 'raza', 'edad_anios', 'edad_unidad',
    'fecha_nacimiento', 'tamano', 'peso', 'sexo',
    'descripcion', 'estado', 'foto',
    'nivel_energia', 'nivel_independencia', 'nivel_complejidad',
    'nivel_sociabilidad', 'apta_ninos', 'costo_estimado_mensual',
    'historial_vacunas', 'carnet_vacunas', 'historia_mascota', 'info_adicional',
]


class MascotaSerializer(serializers.ModelSerializer):
    registrado_por_email = serializers.SerializerMethodField(read_only=True)
    foto_url = serializers.SerializerMethodField(read_only=True)
    carnet_vacunas_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Mascota
        fields = [
            'id', 'nombre', 'especie', 'raza', 'edad_anios', 'edad_unidad',
            'fecha_nacimiento', 'tamano', 'peso', 'sexo',
            'descripcion', 'estado', 'foto', 'foto_url',
            'nivel_energia', 'nivel_independencia', 'nivel_complejidad',
            'nivel_sociabilidad', 'apta_ninos', 'costo_estimado_mensual',
            'historial_vacunas', 'carnet_vacunas', 'carnet_vacunas_url',
            'historia_mascota', 'info_adicional',
            'registrado_por', 'registrado_por_email',
            'fecha_ingreso', 'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'registrado_por', 'fecha_ingreso', 'fecha_actualizacion']
        extra_kwargs = {
            'foto': {'write_only': True, 'required': False},
            'carnet_vacunas': {'write_only': True, 'required': False},
        }

    def get_registrado_por_email(self, obj):
        return obj.registrado_por.email if obj.registrado_por else None

    def get_foto_url(self, obj):
        if not obj.foto or not obj.foto.name:
            return None
        if getattr(settings, 'USE_CLOUDINARY', False):
            return _cloudinary_url(obj.foto.name, 'image')
        url = obj.foto.url
        if url.startswith('http'):
            return url
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url

    def get_carnet_vacunas_url(self, obj):
        if not obj.carnet_vacunas or not obj.carnet_vacunas.name:
            return None
        if getattr(settings, 'USE_CLOUDINARY', False):
            return _cloudinary_url(obj.carnet_vacunas.name, 'raw')
        url = obj.carnet_vacunas.url
        if url.startswith('http'):
            return url
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url


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
