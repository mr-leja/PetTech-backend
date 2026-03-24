# GitHub Copilot Instructions — PetTech MVP

## 1. Contexto del Proyecto (OBLIGATORIO)

PetTech es una plataforma web de adopción responsable de mascotas.
Permite emparejar mascotas disponibles con familias adoptantes según compatibilidad
de hogar, y genera calendarios de vacunación post-adopción automáticamente.

Proyecto **Greenfield** — no hay código legado que preservar.

---

## 2. Arquitectura (NO VIOLAR)

### Modelo de despliegue
**Monolito Modular** + **Clean Architecture** + **API REST**
- Un único proceso Django con módulos internos bien delimitados
- Sin llamadas HTTP entre módulos — toda coordinación es Python interno

### Backend — Bounded Contexts
```
backend/apps/
  mascotas/     → HU-01, 02, 03, 06, 07
  familias/     → HU-04, 05
  solicitudes/  → HU-08, 09, 10, 11
  adopciones/   → HU-12, 13
  calendarios/  → HU-14, 15
  auth/         → roles: Administrador / FamiliaAdoptante
```

### Capas dentro de cada app (Regla de Dependencia — Clean Architecture)
```
interfaces/     → views.py (solo HTTP), serializers.py (DTOs)
use_cases/      → lógica de aplicación, orquestación
domain/         → entidades puras (dataclasses), excepciones de dominio
infrastructure/ → models.py (ORM Django), repositories.py, adapters (S3)
```

**Prohibido:**
- Lógica de negocio en `views.py`
- Imports de Django ORM en `domain/` o `use_cases/`
- Un módulo importando `models.py` de otro módulo directamente
- Guardar archivos de fotos en el servidor — solo URLs en BD (S3/MinIO)

### Frontend
- React 18 + TypeScript (strict) + Axios + TanStack Query
- Organizado por features: `frontend/src/features/{dominio}/`
- `shared/` para componentes, hooks y cliente HTTP reutilizables

### Base de Datos
- **PostgreSQL 16** — una sola instancia compartida entre apps Django
- `@transaction.atomic` para cambios de estado críticos
- `select_for_update()` obligatorio al cambiar estado de mascota (HU-08, concurrencia)

### Docker
- 4 servicios: `db` (PostgreSQL 16), `backend` (Django+Gunicorn), `frontend` (React+Nginx), `minio` (S3 local)
- NUNCA usar `latest` — versiones explícitas en todas las imágenes

---

## 3. Reglas de Negocio Críticas (SIEMPRE PRESERVAR)

### Máquina de Estados — Mascota
- `disponible` → `en_proceso_adopcion` → `adoptada`
- La transición `disponible → en_proceso` ocurre **atómicamente** al crear solicitud (HU-08)
- Si solicitud es `rechazada`, la mascota vuelve a `disponible` (HU-10)

### Máquina de Estados — Solicitud
- `pendiente` → `aprobada` | `rechazada`
- Una solicitud `aprobada` o `rechazada` **NO puede cambiar de estado** → error 409
- Mensaje: `"La decisión sobre esta solicitud ya fue registrada y no puede modificarse"`

### Precondiciones para crear solicitud (HU-08)
- La familia **DEBE** tener `condiciones_hogar` registradas
- La mascota **DEBE** estar en estado `disponible`

### Validaciones de datos
- `edad` de familia adoptante: `>= 18` años
- `especie` de mascota: listado permitido (perro, gato, conejo, etc.)
- `estado_vacunacion`: campo obligatorio en salud
- Fotos: solo JPG/PNG, máximo 5 MB, almacenar **solo URL** en BD

### Calendario de vacunas (HU-14)
- Se genera **automáticamente** al confirmar adopción (HU-12)
- Perros: Parvovirus, Moquillo, Rabia
- Gatos: Panleucopenia, Calicivirus, Rabia
- Cachorro: refuerzos cada 3-4 semanas | Adulto: refuerzos anuales/trianuales
- NO duplicar vacunas ya aplicadas (consultar `salud_mascota`)

---

## 4. Seguridad (OBLIGATORIO — OWASP Top 10)

- Autenticación **JWT** — validada exclusivamente en el backend (`core/permissions.py`)
- Control de acceso por rol: `IsAdministrador` en endpoints de solicitudes, adopciones y decisiones
- NUNCA exponer secretos en variables de entorno del frontend
- NUNCA confiar en el frontend para validaciones de negocio o transiciones de estado
- Usar `django-environ` para gestión de secretos via `.env`
- CORS configurado explícitamente — no usar `CORS_ALLOW_ALL_ORIGINS = True` en producción
- Archivos subidos: validar formato y tamaño **antes** del upload a S3/MinIO

---

## 5. Principios SOLID (Aplicación Concreta)

| Principio | Regla en PetTech |
|---|---|
| **S** — SRP | `views.py` solo HTTP. Lógica de negocio en `use_cases/` |
| **O** — OCP | Nuevas especies/estados sin modificar use_cases existentes |
| **L** — LSP | Serializers heredan de base DRF sin romper comportamientos |
| **I** — ISP | Servicios separados por dominio — nunca un "GodService" |
| **D** — DIP | Use cases dependen de interfaces de repositorio, no del ORM directo |

---


Copilot MUST NOT:
- Leave secrets exposed
- Trust the frontend for authorization or state validation
- Silence or ignore security-related failures

---