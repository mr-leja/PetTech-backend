from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.usuarios.infrastructure.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['email', 'nombre', 'rol', 'perfil_completo', 'is_active']
    list_filter = ['rol', 'is_active', 'perfil_completo']
    search_fields = ['email', 'nombre']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'rol', 'perfil_completo')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'rol'),
        }),
    )
