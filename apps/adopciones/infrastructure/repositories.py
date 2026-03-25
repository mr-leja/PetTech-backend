from apps.adopciones.infrastructure.models import SolicitudAdopcion, Adopcion


class SolicitudRepository:
    def listar_todas(self):
        return SolicitudAdopcion.objects.select_related(
            'mascota', 'familia', 'familia__usuario'
        ).all()

    def listar_por_familia(self, familia_id: int):
        return SolicitudAdopcion.objects.select_related(
            'mascota', 'familia'
        ).filter(familia_id=familia_id)

    def obtener_por_id(self, solicitud_id: int):
        try:
            return SolicitudAdopcion.objects.select_related(
                'mascota', 'familia', 'familia__usuario', 'familia__condiciones_hogar'
            ).get(pk=solicitud_id)
        except SolicitudAdopcion.DoesNotExist:
            return None

    def crear(self, mascota, familia, mensaje: str = '') -> SolicitudAdopcion:
        return SolicitudAdopcion.objects.create(
            mascota=mascota,
            familia=familia,
            estado='PENDIENTE',
            mensaje=mensaje,
        )

    def ids_mascotas_en_proceso_para_familia(self, familia_id: int):
        return set(
            SolicitudAdopcion.objects.filter(
                familia_id=familia_id,
                estado='PENDIENTE',
            ).values_list('mascota_id', flat=True)
        )

    def contadores_familia(self, familia_id: int) -> dict:
        en_proceso = SolicitudAdopcion.objects.filter(
            familia_id=familia_id, estado='PENDIENTE'
        ).count()
        realizadas = SolicitudAdopcion.objects.filter(
            familia_id=familia_id, estado='APROBADA'
        ).count()
        return {'adopciones_en_proceso': en_proceso, 'adopciones_realizadas': realizadas}


class AdopcionRepository:
    def crear(self, solicitud: SolicitudAdopcion, notas: str = '') -> Adopcion:
        return Adopcion.objects.create(solicitud=solicitud, notas=notas)

    def listar_todas(self):
        return Adopcion.objects.select_related(
            'solicitud__mascota', 'solicitud__familia'
        ).all()
