---
applyTo: "backend/**/*.py"
---

> **Scope**: Se aplica al backend de PetTech. Stack: **Django 5 + Django REST Framework + PostgreSQL 16**, arquitectura **Clean Architecture** (domain / infrastructure / interfaces).

# Instrucciones para Archivos de Backend (Python/Django 5 + DRF)

## Stack

| Componente | Tecnología |
|---|---|
| Framework | Django 5 + Django REST Framework 3.15 |
| Base de datos | PostgreSQL 16 (psycopg2-binary) |
| Auth | JWT via `djangorestframework-simplejwt` |
| Almacenamiento | Cloudinary (producción) / Filesystem local (desarrollo) |
| Contenerización | Docker + Docker Compose |

## Directorio de trabajo

```
MVP_PetTech/
  apps/
    adopciones/    ← módulo de adopciones
    familias/      ← módulo de familias adoptantes
    mascotas/      ← catálogo de mascotas del refugio
    usuarios/      ← gestión de usuarios (ADMIN / FAMILIA)
  config/          ← settings, urls.py raíz, asgi/wsgi
  core/            ← permisos, paginación, excepciones globales
```

## Arquitectura en Capas (Clean Architecture)

Cada módulo en `apps/` sigue esta estructura de capas:

```
interfaces/ → domain/ → infrastructure/
```

| Capa | Archivos | Responsabilidad | Prohibido |
|------|---------|-----------------|-----------|
| **`interfaces/`** | `views.py`, `serializers.py`, `urls.py` | HTTP: parsear request, serializar response, registrar ruta | Lógica de negocio, queries directas |
| **`domain/`** | `entities.py`, `exceptions.py` | Entidades de negocio puras, excepciones del dominio | Importar librerías de infraestructura (Django ORM, etc.) |
| **`infrastructure/`** | `models.py` (ORM), `repositories.py` | Persistencia: modelos Django ORM, acceso a PostgreSQL | Lógica de negocio |

## Patrón de acceso a datos (obligatorio)

```python
# interfaces/views.py — delega al repositorio
class MascotaViewSet(viewsets.ModelViewSet):
    serializer_class = MascotaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        repo = MascotaRepository()
        return repo.list_disponibles()
```

```python
# infrastructure/repositories.py — único acceso a la DB
class MascotaRepository:
    def list_disponibles(self):
        return Mascota.objects.filter(disponible=True, deleted_at__isnull=True)
```

NUNCA hacer queries ORM directamente en `views.py`.  
NUNCA importar modelos Django en `domain/`.

## Convenciones de Código

- Nombres en `snake_case` para funciones y variables.
- Modelos Django en `infrastructure/models.py`; entidades de dominio en `domain/entities.py`.
- Serializers DRF en `interfaces/serializers.py`.
- Rutas registradas en `interfaces/urls.py` y montadas en `config/urls.py`.
- Importar settings siempre desde `django.conf.settings`.
- `created_at` / `updated_at` en todo modelo de negocio (`auto_now_add`, `auto_now`).
- Soft delete con campo `deleted_at` (nullable, no borrado físico).
- Roles de usuario: `ADMIN` | `FAMILIA` (campo `rol` en modelo `Usuario`).

## Nuevas Rutas / Módulos

Para agregar un nuevo endpoint:
1. Crear/actualizar el serializer en `interfaces/serializers.py`.
2. Crear/actualizar la vista en `interfaces/views.py`.
3. Registrar la URL en `interfaces/urls.py`.
4. Incluir `interfaces/urls.py` en `config/urls.py` con el prefijo `/api/v1/`.

## Nunca hacer

- Lógica de negocio en `views.py` — delegar a repositorios o entidades de dominio.
- Importar modelos ORM en `domain/`.
- Soft delete físico (usar `deleted_at`).
- Credenciales hardcodeadas — usar variables de entorno (`django-environ`).

---

> Para estándares de código limpio, SOLID, nombrado, API REST, seguridad y observabilidad, ver `.github/docs/lineamientos/dev-guidelines.md`.
