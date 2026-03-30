"""
Tests — SPEC-001: Validaciones de correo electrónico y contraseña.
Covers: formato inválido, email duplicado, normalización, vacío, longitud máxima,
        complejidad de contraseña (HU-03).
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

Usuario = get_user_model()

REGISTRO_URL = '/api/v1/auth/registro/'


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def usuario_existente(db):
    return Usuario.objects.create_user(
        email='existente@pettech.com',
        password='Password123!',
        rol='FAMILIA',
    )


# ---------------------------------------------------------------------------
# CRITERIO-1.2 / HU-01 Error Path: formato inválido
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_registro_email_invalido_sin_arroba(api_client):
    """CRITERIO-1.2: correo sin '@' → 400 con mensaje en español."""
    payload = {'email': 'notanemail', 'password': 'Password123!', 'password_confirm': 'Password123!'}
    response = api_client.post(REGISTRO_URL, payload, format='json')

    assert response.status_code == 400
    error = response.data.get('error', {})
    assert 'email' in error
    assert 'Ingresa un correo electrónico válido.' in error['email']


@pytest.mark.django_db
def test_registro_email_invalido_sin_dominio(api_client):
    """CRITERIO-1.2: correo sin dominio → 400 con mensaje en español."""
    payload = {'email': 'user@', 'password': 'Password123!', 'password_confirm': 'Password123!'}
    response = api_client.post(REGISTRO_URL, payload, format='json')

    assert response.status_code == 400
    error = response.data.get('error', {})
    assert 'email' in error
    assert 'Ingresa un correo electrónico válido.' in error['email']


# ---------------------------------------------------------------------------
# CRITERIO-1.3 / HU-01 Error Path: email duplicado
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_registro_email_duplicado(api_client, usuario_existente):
    """CRITERIO-1.3: email ya registrado → 400 con mensaje amigable en español."""
    payload = {
        'email': 'existente@pettech.com',
        'password': 'OtraPassword123!',
        'password_confirm': 'OtraPassword123!',
    }
    response = api_client.post(REGISTRO_URL, payload, format='json')

    assert response.status_code == 400
    error = response.data.get('error', {})
    assert 'email' in error
    assert 'Este correo ya está registrado.' in error['email']


# ---------------------------------------------------------------------------
# CRITERIO-1.1 / HU-01 Happy Path: registro exitoso
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_registro_email_valido_y_unico(api_client):
    """CRITERIO-1.1: correo válido y único → 201 creado."""
    payload = {
        'email': 'nuevo@pettech.com',
        'password': 'Password123!',
        'password_confirm': 'Password123!',
    }
    response = api_client.post(REGISTRO_URL, payload, format='json')

    assert response.status_code == 201


# ---------------------------------------------------------------------------
# CRITERIO-1.5 / HU-01 Edge Case: normalización
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_registro_email_normalizado_trim_lowercase(api_client):
    """CRITERIO-1.5: email con espacios y mayúsculas → guardado normalizado."""
    payload = {
        'email': '  NUEVO@PETTECH.COM  ',
        'password': 'Password123!',
        'password_confirm': 'Password123!',
    }
    response = api_client.post(REGISTRO_URL, payload, format='json')

    assert response.status_code == 201
    assert Usuario.objects.filter(email='nuevo@pettech.com').exists()


# ---------------------------------------------------------------------------
# CRITERIO-1.4 / HU-01 Error Path: email vacío
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_registro_email_vacio(api_client):
    """CRITERIO-1.4: email vacío → 400."""
    payload = {'email': '', 'password': 'Password123!', 'password_confirm': 'Password123!'}
    response = api_client.post(REGISTRO_URL, payload, format='json')

    assert response.status_code == 400
    error = response.data.get('error', {})
    assert 'email' in error


# ---------------------------------------------------------------------------
# CRITERIO-1.6 / HU-01 Edge Case: longitud máxima
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_registro_email_supera_254_caracteres(api_client):
    """CRITERIO-1.6: email de 255 chars → 400."""
    local = 'a' * 244  # 244 + len('@b.com') = 250+ chars
    payload = {
        'email': f'{local}@example.com',
        'password': 'Password123!',
        'password_confirm': 'Password123!',
    }
    assert len(payload['email']) > 254
    response = api_client.post(REGISTRO_URL, payload, format='json')

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# CRITERIO-3.2 / HU-03 Error Path: contraseña sin carácter especial
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_registro_password_sin_especial(api_client):
    """CRITERIO-3.2: contraseña sin carácter especial → 400 con mensaje de complejidad."""
    payload = {'email': 'nuevo@pettech.com', 'password': 'MiClave1', 'password_confirm': 'MiClave1'}
    response = api_client.post(REGISTRO_URL, payload, format='json')

    assert response.status_code == 400
    error = response.data.get('error', {})
    assert 'password' in error
    assert 'La contraseña debe incluir al menos una letra, un número y un carácter especial.' in error['password']


# ---------------------------------------------------------------------------
# CRITERIO-3.3 / HU-03 Error Path: contraseña sin número
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_registro_password_sin_numero(api_client):
    """CRITERIO-3.3: contraseña sin número → 400 con mensaje de complejidad."""
    payload = {'email': 'nuevo@pettech.com', 'password': 'MiClave!', 'password_confirm': 'MiClave!'}
    response = api_client.post(REGISTRO_URL, payload, format='json')

    assert response.status_code == 400
    error = response.data.get('error', {})
    assert 'password' in error
    assert 'La contraseña debe incluir al menos una letra, un número y un carácter especial.' in error['password']


# ---------------------------------------------------------------------------
# CRITERIO-3.6 / HU-03 Edge Case: solo números
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_registro_password_solo_numeros(api_client):
    """CRITERIO-3.6: contraseña con solo números → 400 con mensaje de complejidad."""
    payload = {'email': 'nuevo@pettech.com', 'password': '12345678', 'password_confirm': '12345678'}
    response = api_client.post(REGISTRO_URL, payload, format='json')

    assert response.status_code == 400
    error = response.data.get('error', {})
    assert 'password' in error
    assert 'La contraseña debe incluir al menos una letra, un número y un carácter especial.' in error['password']


# ---------------------------------------------------------------------------
# CRITERIO-3.1 / HU-03 Happy Path: contraseña válida (compleja)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_registro_password_valida_cumple_complejidad(api_client):
    """CRITERIO-3.1: contraseña con letra, número y especial → 201 creado."""
    payload = {
        'email': 'seguro@pettech.com',
        'password': 'MiClave1!',
        'password_confirm': 'MiClave1!',
    }
    response = api_client.post(REGISTRO_URL, payload, format='json')

    assert response.status_code == 201
