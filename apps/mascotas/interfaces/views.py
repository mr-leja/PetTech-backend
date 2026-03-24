import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdminOrReadOnly, IsAdministrador
from core.pagination import StandardPagination
from apps.mascotas.infrastructure.models import Mascota
from apps.mascotas.infrastructure.repositories import MascotaRepository
from apps.mascotas.interfaces.serializers import (
    MascotaSerializer,
    MascotaCreateSerializer,
    MascotaUpdateSerializer,
)
from apps.mascotas.domain.exceptions import MascotaNoEncontrada

logger = logging.getLogger(__name__)
repository = MascotaRepository()


class MascotaListCreateView(APIView):
    """GET /api/v1/mascotas/ — lista todas | POST crea (solo ADMIN)"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request):
        estado = request.query_params.get('estado')
        especie = request.query_params.get('especie')
        mascotas = repository.listar(estado=estado, especie=especie)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(mascotas, request)
        serializer = MascotaSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = MascotaCreateSerializer(data=request.data)
        if serializer.is_valid():
            mascota = repository.crear(
                registrado_por=request.user,
                **serializer.validated_data,
            )
            logger.info('Mascota registrada: %s por %s', mascota.nombre, request.user.email)
            return Response(
                MascotaSerializer(mascota, context={'request': request}).data,
                status=status.HTTP_201_CREATED,
            )
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class MascotaDetailView(APIView):
    """GET /api/v1/mascotas/{id}/ | PATCH | DELETE (solo ADMIN paramétrico)"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated]

    def _get_mascota(self, pk):
        mascota = repository.obtener_por_id(pk)
        if not mascota:
            raise MascotaNoEncontrada()
        return mascota

    def get(self, request, pk):
        mascota = self._get_mascota(pk)
        serializer = MascotaSerializer(mascota, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        if request.user.rol != 'ADMIN':
            return Response({'error': 'Solo el administrador puede editar mascotas.'}, status=status.HTTP_403_FORBIDDEN)
        mascota = self._get_mascota(pk)
        serializer = MascotaUpdateSerializer(mascota, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(MascotaSerializer(mascota, context={'request': request}).data)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.rol != 'ADMIN':
            return Response({'error': 'Solo el administrador puede eliminar mascotas.'}, status=status.HTTP_403_FORBIDDEN)
        mascota = self._get_mascota(pk)
        if mascota.estado == 'ADOPTADO':
            return Response(
                {'error': 'No se puede eliminar una mascota adoptada.'},
                status=status.HTTP_409_CONFLICT,
            )
        repository.eliminar(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
