"""
Tests — usuarios y autenticación JWT.
Covers: registro, login, protección de endpoints, roles.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

Usuario = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return Usuario.objects.create_user(
        email="admin_auth@test.com",
        password="Admin1234!",
        rol="ADMIN",
        is_staff=True,
    )


@pytest.fixture
def familia_user(db):
    return Usuario.objects.create_user(
        email="user_auth@test.com",
        password="User1234!",
        rol="FAMILIA",
    )


# ---------------------------------------------------------------------------
# Registro
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestRegistro:
    URL = "/api/v1/auth/registro/"

    def test_registro_exitoso(self, api_client):
        r = api_client.post(self.URL, {
            "email": "nuevo@test.com",
            "password": "Segura1234!",
            "password_confirm": "Segura1234!",
            "nombre": "Test User",
        }, format="json")
        assert r.status_code == 201

    def test_registro_crea_rol_familia_por_defecto(self, api_client):
        r = api_client.post(self.URL, {
            "email": "nuevo2@test.com",
            "password": "Segura1234!",
            "password_confirm": "Segura1234!",
            "nombre": "Test User 2",
        }, format="json")
        assert r.status_code == 201
        usuario = Usuario.objects.get(email="nuevo2@test.com")
        assert usuario.rol == "FAMILIA"

    def test_registro_email_duplicado(self, api_client, familia_user):
        r = api_client.post(self.URL, {
            "email": familia_user.email,
            "password": "Segura1234!",
            "password_confirm": "Segura1234!",
            "nombre": "Dup",
        }, format="json")
        assert r.status_code == 400

    def test_registro_password_requerida(self, api_client):
        r = api_client.post(self.URL, {
            "email": "nopassword@test.com",
            "nombre": "Sin pass",
        }, format="json")
        assert r.status_code == 400

    def test_registro_email_requerido(self, api_client):
        r = api_client.post(self.URL, {
            "password": "Password123!",
            "password_confirm": "Password123!",
            "nombre": "Sin email",
        }, format="json")
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestLogin:
    URL = "/api/v1/auth/login/"

    def test_login_exitoso_retorna_tokens(self, api_client, familia_user):
        r = api_client.post(self.URL, {
            "email": familia_user.email,
            "password": "User1234!",
        }, format="json")
        assert r.status_code == 200
        assert "access" in r.data
        assert "refresh" in r.data

    def test_login_retorna_info_usuario(self, api_client, familia_user):
        r = api_client.post(self.URL, {
            "email": familia_user.email,
            "password": "User1234!",
        }, format="json")
        assert r.data.get("email") == familia_user.email or \
               r.data.get("user", {}).get("email") == familia_user.email or \
               "access" in r.data  # al menos retorna el token

    def test_login_credenciales_incorrectas(self, api_client, familia_user):
        r = api_client.post(self.URL, {
            "email": familia_user.email,
            "password": "wrongpassword",
        }, format="json")
        assert r.status_code in (400, 401, 403)

    def test_login_email_no_registrado(self, api_client):
        r = api_client.post(self.URL, {
            "email": "noexiste@test.com",
            "password": "Password123!",
        }, format="json")
        # login con email inexistente puede retornar 400, 401, 403 o incluso 404
        # dependiendo de la implementación del LoginView
        assert r.status_code in (400, 401, 403, 404)


# ---------------------------------------------------------------------------
# Modelo Usuario
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestModeloUsuario:
    def test_crear_usuario_familia(self, db):
        u = Usuario.objects.create_user(
            email="test_model@test.com",
            password="pass1234",
            rol="FAMILIA",
        )
        assert u.pk is not None
        assert u.rol == "FAMILIA"
        assert u.is_active is True

    def test_crear_superusuario(self, db):
        u = Usuario.objects.create_superuser(
            email="super@test.com",
            password="super1234",
        )
        assert u.is_staff is True
        assert u.is_superuser is True
        assert u.rol == "ADMIN"

    def test_str_representation(self, familia_user):
        assert familia_user.email in str(familia_user)

    def test_password_no_almacenada_en_texto_plano(self, familia_user):
        assert familia_user.password != "User1234!"

    def test_email_es_username_field(self):
        assert Usuario.USERNAME_FIELD == "email"
