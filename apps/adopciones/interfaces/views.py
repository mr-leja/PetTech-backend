import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdministrador
from apps.adopciones.infrastructure.repositories import SolicitudRepository, AdopcionRepository, CalendarioRepository
from apps.adopciones.interfaces.serializers import (
    SolicitudAdopcionSerializer,
    SolicitudAdopcionCreateSerializer,
    AdopcionSerializer,
    CalendarioVacunacionSerializer,
    EntradaCalendarioSerializer,
    MarcarVacunaAplicadaSerializer,
)
from apps.adopciones.domain.exceptions import (
    SolicitudNoEncontrada,
    MascotaNoDisponible,
    SolicitudYaDecidida,
    FamiliaRequerida,
)

from apps.adopciones.domain.vaccination import schedule_generator

logger = logging.getLogger(__name__)
solicitud_repo = SolicitudRepository()
adopcion_repo = AdopcionRepository()
calendario_repo = CalendarioRepository()


class SolicitudAdopcionListCreateView(APIView):
    """
    GET  /api/v1/solicitudes/  — ADMIN ve todas; FAMILIA ve las suyas.
    POST /api/v1/solicitudes/  — FAMILIA crea una solicitud (HU-08).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.rol == 'ADMIN':
            solicitudes = solicitud_repo.listar_todas()
        else:
            try:
                familia = user.familia
            except Exception:
                return Response({'results': [], 'count': 0})
            solicitudes = solicitud_repo.listar_por_familia(familia.id)

        serializer = SolicitudAdopcionSerializer(
            solicitudes, many=True, context={'request': request}
        )
        return Response({'results': serializer.data, 'count': solicitudes.count()})

    def post(self, request):
        if request.user.rol == 'ADMIN':
            return Response(
                {'error': 'El administrador no puede crear solicitudes de adopción.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            familia = request.user.familia
        except Exception:
            raise FamiliaRequerida()

        serializer = SolicitudAdopcionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        mascota = serializer.validated_data['mascota']
        if mascota.estado != 'DISPONIBLE':
            raise MascotaNoDisponible()

        solicitud = solicitud_repo.crear(
            mascota=mascota,
            familia=familia,
            mensaje=serializer.validated_data.get('mensaje', ''),
        )

        # Cambiar estado de mascota a EN_PROCESO
        mascota.estado = 'EN_PROCESO'
        mascota.save(update_fields=['estado'])

        logger.info(
            'Solicitud de adopción creada: mascota=%s familia=%s',
            mascota.nombre,
            familia.nombre_familia,
        )
        return Response(
            SolicitudAdopcionSerializer(solicitud, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class SolicitudAdopcionDecisionView(APIView):
    """
    POST /api/v1/solicitudes/{pk}/aprobar/   — ADMIN aprueba (HU-10).
    POST /api/v1/solicitudes/{pk}/rechazar/  — ADMIN rechaza (HU-10).
    """
    permission_classes = [IsAuthenticated, IsAdministrador]

    def _get_solicitud(self, pk):
        solicitud = solicitud_repo.obtener_por_id(pk)
        if not solicitud:
            raise SolicitudNoEncontrada()
        return solicitud

    def post(self, request, pk, accion):
        solicitud = self._get_solicitud(pk)

        if solicitud.estado != 'PENDIENTE':
            raise SolicitudYaDecidida()

        if accion == 'aprobar':
            solicitud.estado = 'APROBADA'
            solicitud.fecha_decision = timezone.now()
            solicitud.notas_admin = request.data.get('notas_admin', '')
            solicitud.save()

            # Mascota → ADOPTADO
            mascota = solicitud.mascota
            mascota.estado = 'ADOPTADO'
            mascota.save(update_fields=['estado'])

            # Registrar adopción realizada
            adopcion = adopcion_repo.crear(solicitud=solicitud)

            # Generar calendario de vacunación automáticamente (HU-14)
            try:
                calendario_generado = schedule_generator.generate(
                    especie=mascota.especie,
                    edad_anios=mascota.edad_anios,
                    edad_unidad=mascota.edad_unidad,
                    historial_vacunas=mascota.historial_vacunas or [],
                    fecha_adopcion=adopcion.fecha_adopcion.date(),
                )
                calendario_repo.crear_con_entradas(
                    adopcion=adopcion,
                    vacunas=calendario_generado.vacunas,
                    notas=calendario_generado.notas,
                )
                logger.info(
                    'Calendario de vacunación generado para adopción #%s (%d vacunas).',
                    adopcion.id,
                    len(calendario_generado.vacunas),
                )
            except Exception:
                logger.exception(
                    'Error al generar el calendario de vacunación para adopción #%s.',
                    adopcion.id,
                )

            logger.info(
                'Solicitud #%s aprobada. Mascota %s adoptada por %s.',
                solicitud.id,
                mascota.nombre,
                solicitud.familia.nombre_familia,
            )

        elif accion == 'rechazar':
            solicitud.estado = 'RECHAZADA'
            solicitud.fecha_decision = timezone.now()
            solicitud.notas_admin = request.data.get('notas_admin', '')
            solicitud.save()

            # Mascota → DISPONIBLE
            mascota = solicitud.mascota
            mascota.estado = 'DISPONIBLE'
            mascota.save(update_fields=['estado'])

            logger.info(
                'Solicitud #%s rechazada. Mascota %s vuelve a DISPONIBLE.',
                solicitud.id,
                mascota.nombre,
            )
        else:
            return Response(
                {'error': 'Acción inválida. Use "aprobar" o "rechazar".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(SolicitudAdopcionSerializer(solicitud, context={'request': request}).data)


class SolicitudAdopcionDetailView(APIView):
    """GET /api/v1/solicitudes/{pk}/ — ADMIN o la familia propietaria (HU-09)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        solicitud = solicitud_repo.obtener_por_id(pk)
        if not solicitud:
            raise SolicitudNoEncontrada()

        user = request.user
        if user.rol != 'ADMIN':
            try:
                if solicitud.familia.usuario_id != user.id:
                    return Response(
                        {'error': 'No tienes permiso para ver esta solicitud.'},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Exception:
                return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(SolicitudAdopcionSerializer(solicitud, context={'request': request}).data)

    def delete(self, request, pk):
        """DELETE /api/v1/solicitudes/{pk}/ — La familia cancela su solicitud PENDIENTE."""
        solicitud = solicitud_repo.obtener_por_id(pk)
        if not solicitud:
            raise SolicitudNoEncontrada()

        user = request.user
        if user.rol == 'ADMIN':
            return Response(
                {'error': 'El administrador no puede cancelar solicitudes de familia.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            if solicitud.familia.usuario_id != user.id:
                return Response(
                    {'error': 'No tienes permiso para cancelar esta solicitud.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Exception:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if solicitud.estado != 'PENDIENTE':
            return Response(
                {'error': 'Solo puedes cancelar solicitudes que estén pendientes de revisión.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mascota = solicitud.mascota
        mascota.estado = 'DISPONIBLE'
        mascota.save(update_fields=['estado'])

        solicitud.delete()

        logger.info(
            'Solicitud cancelada por familia. Mascota %s vuelve a DISPONIBLE.',
            mascota.nombre,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdopcionListView(APIView):
    """GET /api/v1/adopciones/ — ADMIN ve todas; FAMILIA ve las suyas."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.rol == 'ADMIN':
            adopciones = adopcion_repo.listar_todas()
        else:
            try:
                familia = user.familia
            except Exception:
                return Response({'results': [], 'count': 0})
            adopciones = adopcion_repo.listar_todas().filter(
                solicitud__familia=familia
            )

        serializer = AdopcionSerializer(adopciones, many=True, context={'request': request})
        return Response({'results': serializer.data, 'count': adopciones.count()})


class ContadoresFamiliaView(APIView):
    """GET /api/v1/solicitudes/mis-contadores/ — contadores para familia autenticada."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.rol == 'ADMIN':
            return Response({'adopciones_en_proceso': 0, 'adopciones_realizadas': 0})
        try:
            familia = request.user.familia
        except Exception:
            return Response({'adopciones_en_proceso': 0, 'adopciones_realizadas': 0})

        contadores = solicitud_repo.contadores_familia(familia.id)
        return Response(contadores)


class CalendarioVacunacionView(APIView):
    """
    GET /api/v1/adopciones/<adopcion_id>/calendario/ — HU-15.

    - ADMIN: accede a cualquier calendario.
    - FAMILIA: sólo accede al calendario de sus propias adopciones.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, adopcion_id: int):
        calendario = calendario_repo.obtener_por_adopcion(adopcion_id)

        if calendario is None:
            return Response(
                {'error': 'Calendario no encontrado para esta adopción.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = request.user
        if user.rol != 'ADMIN':
            try:
                familia = user.familia
                if calendario.adopcion.solicitud.familia_id != familia.id:
                    return Response(
                        {'error': 'No tienes permiso para ver este calendario.'},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Exception:
                return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = CalendarioVacunacionSerializer(calendario, context={'request': request})
        return Response(serializer.data)


class MarcarVacunaAplicadaView(APIView):
    """
    PATCH /api/v1/adopciones/entradas/<entrada_id>/aplicar/

    Marca una entrada del calendario como completada y guarda el comprobante.
    - FAMILIA: sólo puede marcar entradas de sus propias adopciones.
    - ADMIN: puede marcar cualquier entrada.
    La foto del comprobante es obligatoria.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, entrada_id: int):
        from apps.adopciones.infrastructure.models import EntradaCalendario

        try:
            entrada = EntradaCalendario.objects.select_related(
                'calendario__adopcion__solicitud__familia__usuario'
            ).get(pk=entrada_id)
        except EntradaCalendario.DoesNotExist:
            return Response({'error': 'Entrada no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.rol != 'ADMIN':
            try:
                familia = user.familia
                if entrada.calendario.adopcion.solicitud.familia_id != familia.id:
                    return Response(
                        {'error': 'No tienes permiso para actualizar esta entrada.'},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Exception:
                return Response(status=status.HTTP_403_FORBIDDEN)

        if entrada.completada:
            return Response({'error': 'Esta vacuna ya fue marcada como aplicada.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MarcarVacunaAplicadaSerializer(
            entrada, data=request.data, partial=True, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(completada=True)

        entrada.refresh_from_db()
        return Response(
            EntradaCalendarioSerializer(entrada, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )
