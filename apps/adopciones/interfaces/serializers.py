from rest_framework import serializers
from apps.adopciones.infrastructure.models import SolicitudAdopcion, Adopcion, CalendarioVacunacion, EntradaCalendario


class SolicitudAdopcionSerializer(serializers.ModelSerializer):
    # Mascota — campos completos para evaluación del admin
    mascota_nombre = serializers.CharField(source='mascota.nombre', read_only=True)
    mascota_especie = serializers.CharField(source='mascota.especie', read_only=True)
    mascota_raza = serializers.CharField(source='mascota.raza', read_only=True)
    mascota_edad_anios = serializers.IntegerField(source='mascota.edad_anios', read_only=True)
    mascota_edad_unidad = serializers.CharField(source='mascota.edad_unidad', read_only=True)
    mascota_sexo = serializers.CharField(source='mascota.sexo', read_only=True)
    mascota_tamano = serializers.CharField(source='mascota.tamano', read_only=True)
    mascota_nivel_energia = serializers.CharField(source='mascota.nivel_energia', read_only=True)
    mascota_nivel_independencia = serializers.CharField(source='mascota.nivel_independencia', read_only=True)
    mascota_nivel_complejidad = serializers.CharField(source='mascota.nivel_complejidad', read_only=True)
    mascota_nivel_sociabilidad = serializers.CharField(source='mascota.nivel_sociabilidad', read_only=True)
    mascota_apta_ninos = serializers.BooleanField(source='mascota.apta_ninos', read_only=True, allow_null=True)
    mascota_costo_estimado_mensual = serializers.CharField(source='mascota.costo_estimado_mensual', read_only=True)
    mascota_descripcion = serializers.CharField(source='mascota.descripcion', read_only=True)
    mascota_historia = serializers.CharField(source='mascota.historia_mascota', read_only=True)
    mascota_estado = serializers.CharField(source='mascota.estado', read_only=True)
    mascota_foto_url = serializers.SerializerMethodField()

    # Familia — datos completos del adoptante
    familia_nombre = serializers.CharField(source='familia.nombre_familia', read_only=True)
    familia_cedula = serializers.CharField(source='familia.cedula', read_only=True)
    familia_telefono = serializers.CharField(source='familia.telefono', read_only=True)
    familia_ciudad = serializers.CharField(source='familia.ciudad', read_only=True)
    familia_departamento = serializers.CharField(source='familia.departamento', read_only=True)
    familia_direccion = serializers.CharField(source='familia.direccion', read_only=True)
    familia_email = serializers.CharField(source='familia.usuario.email', read_only=True)
    familia_foto_perfil_url = serializers.SerializerMethodField()
    condiciones_hogar = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudAdopcion
        fields = [
            'id',
            # Mascota
            'mascota', 'mascota_nombre', 'mascota_especie', 'mascota_raza',
            'mascota_edad_anios', 'mascota_edad_unidad', 'mascota_sexo',
            'mascota_tamano', 'mascota_nivel_energia',
            'mascota_nivel_independencia', 'mascota_nivel_complejidad',
            'mascota_nivel_sociabilidad', 'mascota_apta_ninos',
            'mascota_costo_estimado_mensual',
            'mascota_descripcion',
            'mascota_historia', 'mascota_estado', 'mascota_foto_url',
            # Familia / adoptante
            'familia', 'familia_nombre', 'familia_cedula', 'familia_telefono',
            'familia_ciudad', 'familia_departamento', 'familia_direccion',
            'familia_email', 'familia_foto_perfil_url',
            'condiciones_hogar',
            # Solicitud
            'estado', 'mensaje', 'notas_admin',
            'fecha_solicitud', 'fecha_decision',
        ]
        read_only_fields = [
            'id', 'estado', 'notas_admin', 'fecha_solicitud', 'fecha_decision',
        ]

    def get_mascota_foto_url(self, obj):
        request = self.context.get('request')
        if obj.mascota.foto and request:
            return request.build_absolute_uri(obj.mascota.foto.url)
        return None

    def get_familia_foto_perfil_url(self, obj):
        request = self.context.get('request')
        if obj.familia.foto_perfil and request:
            return request.build_absolute_uri(obj.familia.foto_perfil.url)
        return None

    def get_condiciones_hogar(self, obj):
        try:
            ch = obj.familia.condiciones_hogar
            return {
                'tipo_vivienda': ch.tipo_vivienda,
                'propiedad_vivienda': ch.propiedad_vivienda,
                'tiene_patio': ch.tiene_patio,
                'numero_personas': ch.numero_personas,
                'tiene_ninos': ch.tiene_ninos,
                'tamano_hogar': ch.tamano_hogar,
                'tiene_mascotas_actualmente': ch.tiene_mascotas_actualmente,
                'otras_mascotas': ch.otras_mascotas,
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
    # Mascota — detalle completo
    mascota_nombre = serializers.CharField(source='solicitud.mascota.nombre', read_only=True)
    mascota_especie = serializers.CharField(source='solicitud.mascota.especie', read_only=True)
    mascota_raza = serializers.CharField(source='solicitud.mascota.raza', read_only=True)
    mascota_edad_anios = serializers.IntegerField(source='solicitud.mascota.edad_anios', read_only=True)
    mascota_edad_unidad = serializers.CharField(source='solicitud.mascota.edad_unidad', read_only=True)
    mascota_sexo = serializers.CharField(source='solicitud.mascota.sexo', read_only=True)
    mascota_tamano = serializers.CharField(source='solicitud.mascota.tamano', read_only=True)
    mascota_descripcion = serializers.CharField(source='solicitud.mascota.descripcion', read_only=True)
    mascota_foto_url = serializers.SerializerMethodField()

    # Familia / adoptante — detalle completo
    familia_nombre = serializers.CharField(source='solicitud.familia.nombre_familia', read_only=True)
    familia_email = serializers.CharField(source='solicitud.familia.usuario.email', read_only=True)
    familia_cedula = serializers.CharField(source='solicitud.familia.cedula', read_only=True)
    familia_telefono = serializers.CharField(source='solicitud.familia.telefono', read_only=True)
    familia_ciudad = serializers.CharField(source='solicitud.familia.ciudad', read_only=True)
    familia_departamento = serializers.CharField(source='solicitud.familia.departamento', read_only=True)
    familia_foto_perfil_url = serializers.SerializerMethodField()

    # Datos de la solicitud original
    solicitud_mensaje = serializers.CharField(source='solicitud.mensaje', read_only=True)
    solicitud_notas_admin = serializers.CharField(source='solicitud.notas_admin', read_only=True)
    solicitud_fecha = serializers.DateTimeField(source='solicitud.fecha_solicitud', read_only=True)

    class Meta:
        model = Adopcion
        fields = [
            'id', 'solicitud',
            # Mascota
            'mascota_nombre', 'mascota_especie', 'mascota_raza',
            'mascota_edad_anios', 'mascota_edad_unidad', 'mascota_sexo',
            'mascota_tamano', 'mascota_descripcion', 'mascota_foto_url',
            # Familia
            'familia_nombre', 'familia_email', 'familia_cedula',
            'familia_telefono', 'familia_ciudad', 'familia_departamento',
            'familia_foto_perfil_url',
            # Solicitud original
            'solicitud_mensaje', 'solicitud_notas_admin', 'solicitud_fecha',
            # Adopción
            'fecha_adopcion', 'notas',
        ]
        read_only_fields = ['id', 'fecha_adopcion']

    def get_mascota_foto_url(self, obj):
        request = self.context.get('request')
        if obj.solicitud.mascota.foto and request:
            return request.build_absolute_uri(obj.solicitud.mascota.foto.url)
        return None

    def get_familia_foto_perfil_url(self, obj):
        request = self.context.get('request')
        if obj.solicitud.familia.foto_perfil and request:
            return request.build_absolute_uri(obj.solicitud.familia.foto_perfil.url)
        return None


class EntradaCalendarioSerializer(serializers.ModelSerializer):
    foto_comprobante_url = serializers.SerializerMethodField()

    class Meta:
        model = EntradaCalendario
        fields = [
            'id', 'nombre_vacuna', 'descripcion',
            'fecha_sugerida', 'es_refuerzo', 'completada',
            'foto_comprobante_url',
        ]
        read_only_fields = ['id']

    def get_foto_comprobante_url(self, obj):
        request = self.context.get('request')
        if obj.foto_comprobante and request:
            return request.build_absolute_uri(obj.foto_comprobante.url)
        return None


class MarcarVacunaAplicadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntradaCalendario
        fields = ['foto_comprobante']

    def validate_foto_comprobante(self, value):
        if not value:
            raise serializers.ValidationError('La foto del comprobante es obligatoria.')
        return value


class CalendarioVacunacionSerializer(serializers.ModelSerializer):
    entradas = EntradaCalendarioSerializer(many=True, read_only=True)

    # Datos de la mascota (read-only, para contexto en el frontend)
    mascota_nombre = serializers.CharField(
        source='adopcion.solicitud.mascota.nombre', read_only=True
    )
    mascota_especie = serializers.CharField(
        source='adopcion.solicitud.mascota.especie', read_only=True
    )
    mascota_foto_url = serializers.SerializerMethodField()

    class Meta:
        model = CalendarioVacunacion
        fields = [
            'id', 'adopcion',
            'mascota_nombre', 'mascota_especie', 'mascota_foto_url',
            'notas', 'fecha_generacion',
            'entradas',
        ]
        read_only_fields = ['id', 'fecha_generacion']

    def get_mascota_foto_url(self, obj):
        request = self.context.get('request')
        mascota = obj.adopcion.solicitud.mascota
        if mascota.foto and request:
            return request.build_absolute_uri(mascota.foto.url)
        return None
