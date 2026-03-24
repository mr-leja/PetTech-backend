import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.usuarios.interfaces.serializers import RegistroSerializer, UsuarioSerializer
from apps.usuarios.infrastructure.models import Usuario

logger = logging.getLogger(__name__)


class LoginView(TokenObtainPairView):
    """Login — retorna access + refresh tokens con datos del usuario."""
    permission_classes = [AllowAny]


class RegistroView(APIView):
    """Registro de nuevo usuario con rol FAMILIA."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info('Nuevo usuario registrado: %s', user.email)
            return Response(
                {
                    'message': 'Usuario registrado exitosamente. Por favor completa tu perfil.',
                    'user': UsuarioSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PerfilView(APIView):
    """Devuelve, actualiza y elimina el perfil del usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    def delete(self, request):
        user = request.user
        if user.rol == 'ADMIN':
            return Response(
                {'error': 'Los administradores no pueden eliminar su cuenta desde aquí.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        logger.info('Cuenta eliminada por el usuario: %s', user.email)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
