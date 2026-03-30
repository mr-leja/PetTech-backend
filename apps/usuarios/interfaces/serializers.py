import re

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email as django_validate_email
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.usuarios.infrastructure.models import Usuario

_PASSWORD_COMPLEXITY_REGEX = re.compile(
    r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':"|,.<>/?])'
)


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

    def validate_email(self, value: str) -> str:
        value = value.strip().lower()
        try:
            django_validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError('Ingresa un correo electrónico válido.')
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este correo ya está registrado.')
        return value

    def validate_password(self, value: str) -> str:
        if not _PASSWORD_COMPLEXITY_REGEX.search(value):
            raise serializers.ValidationError(
                'La contraseña debe incluir al menos una letra, un número y un carácter especial.'
            )
        return value

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

    def validate_email(self, value: str) -> str:
        value = value.strip().lower()
        try:
            django_validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError('Ingresa un correo electrónico válido.')
        qs = Usuario.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Este correo ya está registrado.')
        return value
