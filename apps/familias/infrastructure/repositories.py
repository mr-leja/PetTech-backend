from django.db import transaction
from apps.familias.infrastructure.models import Familia, CondicionesHogar
from apps.usuarios.infrastructure.models import Usuario


class FamiliaRepository:
    def obtener_por_usuario(self, usuario_id: int):
        try:
            return Familia.objects.select_related('condiciones_hogar').get(usuario_id=usuario_id)
        except Familia.DoesNotExist:
            return None

    def obtener_por_id(self, familia_id: int):
        try:
            return Familia.objects.select_related('condiciones_hogar').get(pk=familia_id)
        except Familia.DoesNotExist:
            return None

    @transaction.atomic
    def crear_familia(self, usuario: Usuario, **kwargs) -> Familia:
        familia = Familia.objects.create(usuario=usuario, **kwargs)
        return familia

    @transaction.atomic
    def registrar_condiciones_hogar(self, familia: Familia, **kwargs) -> CondicionesHogar:
        condiciones = CondicionesHogar.objects.create(familia=familia, **kwargs)
        # Marcar perfil completo si tiene familia + condiciones
        familia.usuario.perfil_completo = True
        familia.usuario.save(update_fields=['perfil_completo'])
        return condiciones

    def listar(self):
        return Familia.objects.select_related('usuario', 'condiciones_hogar').all()
