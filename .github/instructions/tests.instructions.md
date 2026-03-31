---
applyTo: "backend/tests/**/*.py,frontend/src/__tests__/**/*.{js,jsx,ts,tsx}"
---

> **Scope**: Las reglas de backend aplican a tests Python en `MVP_PetTech/apps/*/tests/`; las de frontend aplican a tests TypeScript en `MVP_FrontEnd/src/test/`. Principios (independencia, aislamiento, AAA, cobertura ≥ 80%) aplican a ambos.

# Instrucciones para Archivos de Pruebas Unitarias

## Principios

- **Independencia**: cada test es 100% independiente — sin estado compartido entre tests.
- **Aislamiento**: mockear SIEMPRE dependencias externas (DB, APIs externas, sistema de archivos).
- **Claridad**: nombre del test debe describir la función bajo prueba y el escenario.
- **Cobertura**: cubrir happy path, error path y edge cases para cada unidad.

## Backend (pytest + Django)

### Estructura de archivos

```
MVP_PetTech/apps/<modulo>/tests/
  test_views.py         ← tests de endpoints DRF (APIClient)
  test_repositories.py  ← tests de repositories con DB mockeada
  test_domain.py        ← tests de entidades y excepciones de dominio
```

> Configuración pytest en `MVP_PetTech/pytest.ini`. Fixtures compartidas en `conftest.py` de cada app.

### Convenciones

- Nombre: `test_[función]_[escenario]` (ej: `test_create_mascota_success`, `test_create_mascota_nombre_vacio`)
- Usar `pytest-django` y `APIClient` de DRF para tests de vistas.
- Mockear repositorios en tests de vistas con `unittest.mock.patch` o `MagicMock`.
- Usar `@pytest.mark.django_db` solo en tests que necesiten base de datos real (de integración).
- Para tests unitarios: mockear el ORM, no tocar la DB real.

```python
# Ejemplo mínimo de test de vista (DRF)
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

def test_list_mascotas_unauthenticated():
    client = APIClient()
    response = client.get('/api/v1/mascotas/')
    assert response.status_code == 401

@patch('apps.mascotas.interfaces.views.MascotaRepository')
def test_list_mascotas_success(mock_repo):
    mock_repo.return_value.list_disponibles.return_value = []
    client = APIClient()
    # ... autenticar y verificar 200
```

## Frontend (Vitest + Testing Library)

### Estructura de archivos

```
MVP_FrontEnd/src/test/
  <modulo>.test.ts        ← tests de stores y hooks
  <Feature>Page.test.tsx  ← tests de páginas/componentes
  setup.ts                ← configuración global de tests
```

### Convenciones

- Nombre del describe: nombre del componente/hook.
- Nombre del it/test: `[verbo] [qué hace] [condición]` (ej: `renders mascotas list when authenticated`).
- Usar `vi.mock()` para mockear módulos externos (Axios, stores).
- Siempre limpiar mocks con `beforeEach(() => vi.clearAllMocks())`.
- Tipado TypeScript en todos los archivos de test.

```tsx
// Ejemplo mínimo de test de componente (TypeScript)
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('MascotasPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders loading state initially', () => {
    render(<MascotasPage />);
    expect(screen.getByText(/cargando/i)).toBeInTheDocument();
  });
});
```

## Nunca hacer

- Tests que dependen del orden de ejecución.
- Llamadas reales a la API backend o PostgreSQL desde tests unitarios.
- `console.log` permanentes en tests.
- Lógica condicional dentro de un test (if/else).
- Usar `sleep` para sincronización temporal (cero tests "flaky").
- `any` en TypeScript de tests.

---

> Para quality gates, pirámide de testing, TDD y nomenclatura Gherkin, ver `.github/docs/lineamientos/dev-guidelines.md` §7 y `.github/docs/lineamientos/qa-guidelines.md`.

### Estructura AAA obligatoria
```python
# GIVEN — preparar datos y contexto
# WHEN  — ejecutar la acción bajo prueba
# THEN  — verificar el resultado esperado
```

### DoR de Automatización
Antes de automatizar un flujo, verificar:
- [ ] Caso ejecutado exitosamente en manual sin bugs críticos
- [ ] Caso de prueba detallado con datos identificados
- [ ] Viabilidad técnica comprobada
- [ ] Ambiente estable disponible
- [ ] Aprobación del equipo

### DoD de Automatización
Un script finaliza cuando:
- [ ] Código revisado por pares (pull request review)
- [ ] Datos desacoplados del código
- [ ] Integrado al pipeline de CI
- [ ] Con documentación y trazabilidad hacia la HU
