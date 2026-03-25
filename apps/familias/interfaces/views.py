import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from core.permissions import IsAdministrador
from apps.familias.infrastructure.repositories import FamiliaRepository
from apps.familias.infrastructure.models import Familia
from apps.familias.interfaces.serializers import (
    FamiliaSerializer,
    FamiliaCreateSerializer,
    CondicionesHogarSerializer,
)
from apps.familias.domain.exceptions import (
    FamiliaYaRegistrada,
    CondicionesHogarYaRegistradas,
    FamiliaNoEncontrada,
)

logger = logging.getLogger(__name__)
repository = FamiliaRepository()


class MiFamiliaView(APIView):
    """GET/POST/PATCH /api/v1/familias/mia/ — registro, consulta y edición de la propia familia"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        familia = repository.obtener_por_usuario(request.user.id)
        if not familia:
            return Response({'familia': None, 'tiene_familia': False})
        return Response({'familia': FamiliaSerializer(familia, context={'request': request}).data, 'tiene_familia': True})

    def post(self, request):
        if repository.obtener_por_usuario(request.user.id):
            raise FamiliaYaRegistrada()
        serializer = FamiliaCreateSerializer(data=request.data)
        if serializer.is_valid():
            familia = repository.crear_familia(usuario=request.user, **serializer.validated_data)
            logger.info('Familia registrada para usuario: %s', request.user.email)
            return Response(
                FamiliaSerializer(familia, context={'request': request}).data,
                status=status.HTTP_201_CREATED,
            )
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        familia = repository.obtener_por_usuario(request.user.id)
        if not familia:
            raise FamiliaNoEncontrada()
        serializer = FamiliaCreateSerializer(familia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if request.data.get('borrar_foto_perfil') == 'true' and not serializer.validated_data.get('foto_perfil'):
                if familia.foto_perfil:
                    familia.foto_perfil.delete(save=False)
                familia.foto_perfil = None
                familia.save(update_fields=['foto_perfil'])
            return Response(FamiliaSerializer(familia, context={'request': request}).data)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CondicionesHogarView(APIView):
    """POST /api/v1/familias/mia/condiciones-hogar/ — registra condiciones (HU-05)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        familia = repository.obtener_por_usuario(request.user.id)
        if not familia:
            raise FamiliaNoEncontrada()
        try:
            condiciones = familia.condiciones_hogar
            return Response(CondicionesHogarSerializer(condiciones).data)
        except Exception:
            return Response({'condiciones': None, 'tiene_condiciones': False})

    def post(self, request):
        familia = repository.obtener_por_usuario(request.user.id)
        if not familia:
            return Response(
                {'error': 'Debes registrar tu familia antes de agregar condiciones del hogar.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if hasattr(familia, 'condiciones_hogar') and familia.condiciones_hogar:
            raise CondicionesHogarYaRegistradas()
        serializer = CondicionesHogarSerializer(data=request.data)
        if serializer.is_valid():
            condiciones = repository.registrar_condiciones_hogar(
                familia=familia,
                **serializer.validated_data,
            )
            logger.info('Condiciones de hogar registradas para: %s', request.user.email)
            return Response(
                CondicionesHogarSerializer(condiciones).data,
                status=status.HTTP_201_CREATED,
            )
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        familia = repository.obtener_por_usuario(request.user.id)
        if not familia:
            raise FamiliaNoEncontrada()
        try:
            condiciones = familia.condiciones_hogar
        except Exception:
            raise FamiliaNoEncontrada()
        serializer = CondicionesHogarSerializer(condiciones, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(CondicionesHogarSerializer(condiciones).data)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FamiliaAdminListView(APIView):
    """GET /api/v1/familias/ — solo ADMIN puede listar todas las familias"""
    permission_classes = [IsAuthenticated, IsAdministrador]

    def get(self, request):
        familias = repository.listar()
        serializer = FamiliaSerializer(familias, many=True)
        return Response({'results': serializer.data, 'count': familias.count()})
