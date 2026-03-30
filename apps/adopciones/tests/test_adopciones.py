
import pytest
from datetime import date
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from model_bakery import baker

from apps.adopciones.infrastructure.models import (
    Adopcion,
    CalendarioVacunacion,
)
from apps.adopciones.infrastructure.repositories import (
    SolicitudRepository,
    AdopcionRepository,
    CalendarioRepository,
)
from apps.adopciones.domain.vaccination import VacunaRecomendada

Usuario = get_user_model()

@pytest.fixture
def admin_user(db):
    return Usuario.objects.create_user(
        email="admin@test.com",
        password="Admin1234!",
        rol="ADMIN",
        is_staff=True,
    )

@pytest.fixture
def familia_user(db):
    return Usuario.objects.create_user(
        email="familia@test.com",
        password="Familia1234!",
        rol="FAMILIA",
    )

@pytest.fixture
def familia(db, familia_user):
    return baker.make(
        "familias.Familia",
        usuario=familia_user,
        nombre_familia="Familia Test",
        cedula="12345678",
        telefono="3001234567",
        ciudad="Bogotá",
        departamento="Cundinamarca",
    )

@pytest.fixture
def mascota_disponible(db, admin_user):
    return baker.make(
        "mascotas.Mascota",
        nombre="Luna",
        especie="PERRO",
        edad_anios=3,
        edad_unidad="MESES",
        estado="DISPONIBLE",
        historial_vacunas=[],
        registrado_por=admin_user,
    )


@pytest.fixture
def solicitud_pendiente(db, mascota_disponible, familia):
    return baker.make(
        "adopciones.SolicitudAdopcion",
        mascota=mascota_disponible,
        familia=familia,
        estado="PENDIENTE",
    )


@pytest.fixture
def adopcion(db, solicitud_pendiente):
    solicitud_pendiente.estado = "APROBADA"
    solicitud_pendiente.save()
    return baker.make("adopciones.Adopcion", solicitud=solicitud_pendiente)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def familia_client(api_client, familia_user):
    api_client.force_authenticate(user=familia_user)
    return api_client


# ---------------------------------------------------------------------------
# SolicitudRepository
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSolicitudRepository:
    repo = SolicitudRepository()

    def test_crear_solicitud(self, mascota_disponible, familia):
        sol = self.repo.crear(mascota_disponible, familia, mensaje="Quiero adoptar")
        assert sol.pk is not None
        assert sol.estado == "PENDIENTE"
        assert sol.mascota == mascota_disponible
        assert sol.familia == familia

    def test_listar_todas(self, solicitud_pendiente):
        resultado = self.repo.listar_todas()
        assert solicitud_pendiente in list(resultado)

    def test_listar_por_familia(self, solicitud_pendiente, familia):
        resultado = self.repo.listar_por_familia(familia.id)
        assert solicitud_pendiente in list(resultado)

    def test_obtener_por_id(self, solicitud_pendiente):
        found = self.repo.obtener_por_id(solicitud_pendiente.pk)
        assert found == solicitud_pendiente

    def test_obtener_por_id_no_existe_retorna_none(self):
        assert self.repo.obtener_por_id(99999) is None

    def test_contadores_familia(self, solicitud_pendiente, familia):
        contadores = self.repo.contadores_familia(familia.id)
        assert contadores["adopciones_en_proceso"] == 1
        assert "adopciones_realizadas" in contadores

    def test_ids_mascotas_en_proceso(self, solicitud_pendiente, familia):
        ids = self.repo.ids_mascotas_en_proceso_para_familia(familia.id)
        assert solicitud_pendiente.mascota_id in ids


# ---------------------------------------------------------------------------
# AdopcionRepository
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAdopcionRepository:
    repo = AdopcionRepository()

    def test_crear_adopcion(self, solicitud_pendiente):
        adopcion = self.repo.crear(solicitud=solicitud_pendiente)
        assert adopcion.pk is not None
        assert adopcion.solicitud == solicitud_pendiente

    def test_listar_todas_incluye_adopcion(self, adopcion):
        resultado = self.repo.listar_todas()
        assert adopcion in list(resultado)

    def test_listar_todas_ordenadas_por_fecha(self, db, admin_user, familia):
        mascota1 = baker.make("mascotas.Mascota", estado="DISPONIBLE", registrado_por=admin_user, especie="GATO")
        mascota2 = baker.make("mascotas.Mascota", estado="DISPONIBLE", registrado_por=admin_user, especie="PERRO")
        sol1 = baker.make("adopciones.SolicitudAdopcion", mascota=mascota1, familia=familia, estado="APROBADA")
        sol2 = baker.make("adopciones.SolicitudAdopcion", mascota=mascota2, familia=familia, estado="APROBADA")
        a1 = self.repo.crear(solicitud=sol1)
        a2 = self.repo.crear(solicitud=sol2)
        ids = [a.pk for a in self.repo.listar_todas()]
        assert ids.index(a2.pk) < ids.index(a1.pk)


# ---------------------------------------------------------------------------
# CalendarioRepository
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCalendarioRepository:
    repo = CalendarioRepository()

    def _vacunas_ejemplo(self):
        hoy = date.today()
        return [
            VacunaRecomendada("Rabia", "Antirrábica", hoy, es_refuerzo=False),
            VacunaRecomendada("Parvovirus", "Protege del parvo", hoy, es_refuerzo=False),
        ]

    def test_crear_con_entradas(self, adopcion):
        vacunas = self._vacunas_ejemplo()
        cal = self.repo.crear_con_entradas(adopcion, vacunas, notas="Test")
        assert cal.pk is not None
        assert cal.entradas.count() == 2

    def test_entradas_tienen_datos_correctos(self, adopcion):
        vacunas = self._vacunas_ejemplo()
        cal = self.repo.crear_con_entradas(adopcion, vacunas)
        entrada = cal.entradas.first()
        assert entrada.nombre_vacuna in ["Rabia", "Parvovirus"]
        assert entrada.completada is False

    def test_obtener_por_adopcion(self, adopcion):
        vacunas = self._vacunas_ejemplo()
        cal_creado = self.repo.crear_con_entradas(adopcion, vacunas)
        cal_obtenido = self.repo.obtener_por_adopcion(adopcion.pk)
        assert cal_obtenido.pk == cal_creado.pk

    def test_obtener_por_adopcion_no_existente_retorna_none(self):
        assert self.repo.obtener_por_adopcion(99999) is None

    def test_sin_vacunas_crea_calendario_vacio(self, adopcion):
        cal = self.repo.crear_con_entradas(adopcion, [])
        assert cal.entradas.count() == 0


# ---------------------------------------------------------------------------
# CalendarioVacunacionView — API
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCalendarioVacunacionView:
    URL = "/api/v1/adopciones/{}/calendario/"

    def _crear_calendario(self, adopcion):
        repo = CalendarioRepository()
        vacunas = [
            VacunaRecomendada("Rabia", "Antirrábica", date.today(), es_refuerzo=False),
        ]
        return repo.crear_con_entradas(adopcion, vacunas, notas="Test CI")

    def test_admin_puede_ver_calendario(self, admin_client, adopcion):
        self._crear_calendario(adopcion)
        r = admin_client.get(self.URL.format(adopcion.pk))
        assert r.status_code == 200
        assert "entradas" in r.data

    def test_familia_puede_ver_su_propio_calendario(self, familia_client, adopcion, familia):
        self._crear_calendario(adopcion)
        r = familia_client.get(self.URL.format(adopcion.pk))
        assert r.status_code == 200

    def test_unauthenticated_returns_401(self, api_client, adopcion):
        self._crear_calendario(adopcion)
        r = api_client.get(self.URL.format(adopcion.pk))
        assert r.status_code == 401

    def test_calendario_inexistente_retorna_404(self, admin_client):
        r = admin_client.get(self.URL.format(99999))
        assert r.status_code == 404

    def test_respuesta_contiene_mascota_nombre(self, admin_client, adopcion):
        self._crear_calendario(adopcion)
        r = admin_client.get(self.URL.format(adopcion.pk))
        assert "mascota_nombre" in r.data

    def test_respuesta_contiene_notas(self, admin_client, adopcion):
        self._crear_calendario(adopcion)
        r = admin_client.get(self.URL.format(adopcion.pk))
        assert r.data["notas"] == "Test CI"


# ---------------------------------------------------------------------------
# SolicitudAdopcionDecisionView — generación automática de calendario
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDecisionViewCalendarioAutomatico:
    URL = "/api/v1/solicitudes/{}/aprobar/"

    def test_aprobar_crea_calendario(self, admin_client, solicitud_pendiente):
        r = admin_client.post(
            f"/api/v1/solicitudes/{solicitud_pendiente.pk}/aprobar/",
            {"notas_admin": "Aprobado"},
            format="json",
        )
        assert r.status_code == 200
        adopcion = Adopcion.objects.get(solicitud=solicitud_pendiente)
        assert CalendarioVacunacion.objects.filter(adopcion=adopcion).exists()

    def test_aprobar_crea_entradas_calendario(self, admin_client, solicitud_pendiente):
        admin_client.post(
            f"/api/v1/solicitudes/{solicitud_pendiente.pk}/aprobar/",
            {"notas_admin": "Aprobado"},
            format="json",
        )
        adopcion = Adopcion.objects.get(solicitud=solicitud_pendiente)
        cal = CalendarioVacunacion.objects.get(adopcion=adopcion)
        # Un perro de 3 meses sin historial debe tener al menos 4 vacunas
        assert cal.entradas.count() >= 4

    def test_mascota_pasa_a_estado_adoptado(self, admin_client, solicitud_pendiente, mascota_disponible):
        admin_client.post(
            f"/api/v1/solicitudes/{solicitud_pendiente.pk}/aprobar/",
            {"notas_admin": "Aprobado"},
            format="json",
        )
        mascota_disponible.refresh_from_db()
        assert mascota_disponible.estado == "ADOPTADO"
