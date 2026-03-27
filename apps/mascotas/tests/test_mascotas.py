"""
Tests unitarios — mascotas: modelo, serializer y vistas CRUD.
Cubre: creación, filtros de estado, permisos de admin vs familia.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from model_bakery import baker

Usuario = get_user_model()

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def admin_user(db):
    return Usuario.objects.create_user(
        email="admin_mascotas@test.com",
        password="Admin1234!",
        rol="ADMIN",
        is_staff=True,
    )


@pytest.fixture
def familia_user(db):
    return Usuario.objects.create_user(
        email="familia_mascotas@test.com",
        password="Familia1234!",
        rol="FAMILIA",
    )


@pytest.fixture
def mascota_disponible(db, admin_user):
    return baker.make(
        "mascotas.Mascota",
        nombre="Rex",
        especie="PERRO",
        edad_anios=2,
        edad_unidad="ANIOS",
        estado="DISPONIBLE",
        historial_vacunas=[],
        registrado_por=admin_user,
    )


@pytest.fixture
def mascota_adoptada(db, admin_user):
    return baker.make(
        "mascotas.Mascota",
        nombre="Michi",
        especie="GATO",
        edad_anios=3,
        edad_unidad="ANIOS",
        estado="ADOPTADO",
        historial_vacunas=[],
        registrado_por=admin_user,
    )


@pytest.fixture
def admin_client(db, admin_user):
    c = APIClient()
    c.force_authenticate(user=admin_user)
    return c


@pytest.fixture
def familia_client(db, familia_user):
    c = APIClient()
    c.force_authenticate(user=familia_user)
    return c


# ---------------------------------------------------------------------------
# GET /api/v1/mascotas/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestListadoMascotas:
    URL = "/api/v1/mascotas/"

    def test_familia_puede_listar(self, familia_client, mascota_disponible):
        r = familia_client.get(self.URL)
        assert r.status_code == 200

    def test_admin_puede_listar(self, admin_client, mascota_disponible):
        r = admin_client.get(self.URL)
        assert r.status_code == 200

    def test_unauthenticated_returns_401(self, mascota_disponible):
        r = APIClient().get(self.URL)
        assert r.status_code == 401

    def test_respuesta_tiene_results_y_count(self, admin_client, mascota_disponible):
        r = admin_client.get(self.URL)
        assert "results" in r.data
        assert "count" in r.data

    def test_count_incluye_mascota_creada(self, admin_client, mascota_disponible):
        r = admin_client.get(self.URL)
        assert r.data["count"] >= 1

    def test_filtro_estado_disponible(self, admin_client, mascota_disponible, mascota_adoptada):
        r = admin_client.get(self.URL + "?estado=DISPONIBLE")
        nombres = [m["nombre"] for m in r.data["results"]]
        assert "Rex" in nombres
        assert "Michi" not in nombres

    def test_filtro_especie(self, admin_client, mascota_disponible, mascota_adoptada):
        r = admin_client.get(self.URL + "?especie=GATO")
        assert all(m["especie"] == "GATO" for m in r.data["results"])


# ---------------------------------------------------------------------------
# POST /api/v1/mascotas/  (solo admin)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCrearMascota:
    URL = "/api/v1/mascotas/"

    PAYLOAD = {
        "nombre": "Coco",
        "especie": "PERRO",
        "edad_anios": 2,
        "edad_unidad": "ANIOS",
        "sexo": "MACHO",
        "tamano": "MEDIANO",
        "nivel_energia": "ALTO",
        "nivel_independencia": "MEDIO",
        "nivel_complejidad": "BAJO",
        "nivel_sociabilidad": "ALTO",
        "historial_vacunas": [],
    }

    def test_admin_puede_crear(self, admin_client):
        r = admin_client.post(self.URL, self.PAYLOAD, format="json")
        assert r.status_code == 201

    def test_mascota_creada_estado_disponible(self, admin_client):
        r = admin_client.post(self.URL, self.PAYLOAD, format="json")
        assert r.data["estado"] == "DISPONIBLE"

    def test_familia_no_puede_crear(self, familia_client):
        r = familia_client.post(self.URL, self.PAYLOAD, format="json")
        assert r.status_code in (403, 401)

    def test_nombre_requerido(self, admin_client):
        payload = {**self.PAYLOAD}
        del payload["nombre"]
        r = admin_client.post(self.URL, payload, format="json")
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/v1/mascotas/{id}/
# PUT /api/v1/mascotas/{id}/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDetalleMascota:
    def test_get_mascota_existente(self, admin_client, mascota_disponible):
        r = admin_client.get(f"/api/v1/mascotas/{mascota_disponible.pk}/")
        assert r.status_code == 200
        assert r.data["nombre"] == "Rex"

    def test_get_mascota_no_existente_retorna_404(self, admin_client):
        r = admin_client.get("/api/v1/mascotas/99999/")
        assert r.status_code == 404

    def test_admin_puede_actualizar_mascota(self, admin_client, mascota_disponible):
        r = admin_client.patch(
            f"/api/v1/mascotas/{mascota_disponible.pk}/",
            {"nombre": "RexActualizado"},
            format="json",
        )
        assert r.status_code == 200
        assert r.data["nombre"] == "RexActualizado"

    def test_familia_no_puede_actualizar(self, familia_client, mascota_disponible):
        r = familia_client.patch(
            f"/api/v1/mascotas/{mascota_disponible.pk}/",
            {"nombre": "Intento"},
            format="json",
        )
        assert r.status_code in (403, 401)
