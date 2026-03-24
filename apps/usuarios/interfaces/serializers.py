from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.usuarios.infrastructure.models import Usuario


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT personalizado que agrega rol y perfil_completo al token."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['rol'] = user.rol
        token['perfil_completo'] = user.perfil_completo
        token['nombre'] = user.nombre
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['rol'] = self.user.rol
        data['perfil_completo'] = self.user.perfil_completo
        data['email'] = self.user.email
        data['nombre'] = self.user.nombre
        data['id'] = self.user.id
        return data


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['email', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Las contraseñas no coinciden.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = Usuario.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            rol='FAMILIA',
        )
        return user


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nombre', 'rol', 'perfil_completo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']
