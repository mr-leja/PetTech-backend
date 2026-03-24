from rest_framework.permissions import BasePermission


class IsAdministrador(BasePermission):
    """Permite acceso solo a usuarios con rol ADMIN."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == 'ADMIN'
        )


class IsFamiliaAdoptante(BasePermission):
    """Permite acceso solo a usuarios con rol FAMILIA."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == 'FAMILIA'
        )


class IsAdminOrReadOnly(BasePermission):
    """Admin tiene acceso completo; otros solo lectura."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.rol == 'ADMIN'
