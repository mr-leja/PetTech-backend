from apps.mascotas.infrastructure.models import Mascota


class MascotaRepository:
    def listar(self, estado: str = None, especie: str = None):
        qs = Mascota.objects.all()
        if estado:
            qs = qs.filter(estado=estado)
        if especie:
            qs = qs.filter(especie=especie)
        return qs

    def obtener_por_id(self, mascota_id: int):
        try:
            return Mascota.objects.get(pk=mascota_id)
        except Mascota.DoesNotExist:
            return None

    def guardar(self, mascota: Mascota) -> Mascota:
        mascota.save()
        return mascota

    def crear(self, **kwargs) -> Mascota:
        return Mascota.objects.create(**kwargs)

    def eliminar(self, mascota_id: int) -> bool:
        deleted, _ = Mascota.objects.filter(pk=mascota_id).delete()
        return deleted > 0
