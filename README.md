# PetTech Backend

API REST con Django 5, Clean Architecture, JWT y PostgreSQL.

## Stack
- Python 3.12, Django 5, Django REST Framework
- PostgreSQL 16, MinIO (fotos)
- JWT via `djangorestframework-simplejwt`
- Docker / Docker Compose

## Estructura
```
apps/
  usuarios/    # Custom User, JWT, roles (ADMIN/FAMILIA)
  mascotas/    # Registro y gestión de mascotas
  familias/    # Registro de familias y condiciones del hogar
config/        # Configuración Django (base/development/production)
core/          # Utilidades: permisos, paginación, excepciones
```

## Quick Start con Docker
```bash
cp .env.example .env
docker compose up --build
```
> Al ejecutar migraciones se crea automáticamente `admin@pettech.com / Admin1234!`

## Endpoints principales
| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/v1/auth/login/` | Login - retorna JWT |
| POST | `/api/v1/auth/registro/` | Registro nuevo usuario |
| GET  | `/api/v1/auth/perfil/` | Perfil del usuario autenticado |
| GET  | `/api/v1/mascotas/` | Listar mascotas (con filtros) |
| POST | `/api/v1/mascotas/` | Registrar mascota (solo ADMIN) |
| GET  | `/api/v1/mascotas/{id}/` | Detalle mascota |
| PATCH| `/api/v1/mascotas/{id}/` | Editar mascota (solo ADMIN) |
| POST | `/api/v1/familias/mia/` | Registrar familia (HU-04) |
| GET  | `/api/v1/familias/mia/` | Ver mi familia |
| POST | `/api/v1/familias/mia/condiciones-hogar/` | Registrar hogar (HU-05) |
| GET  | `/api/v1/familias/` | Listar familias (solo ADMIN) |

## Desarrollo local (sin Docker)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements/development.txt
cp .env.example .env  # ajustar DB_HOST=localhost
python manage.py migrate
python manage.py runserver
```
