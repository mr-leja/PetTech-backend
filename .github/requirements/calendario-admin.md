# Requerimiento: Vista de Calendario de Vacunación para el Administrador (Backend)

## Descripción General

El backend necesita un nuevo endpoint que devuelva el **listado de todos los calendarios de vacunación** con un resumen del estado de cada uno, para alimentar la vista de administración `CalendariosAdminPage`.

El endpoint actual `GET /api/v1/adopciones/<adopcion_id>/calendario/` retorna el detalle completo de un solo calendario. Se necesita un endpoint de **listar** con resumen calculado.

## Nuevo Endpoint

### `GET /api/v1/calendarios/`
- **Acceso:** Solo ADMIN (`IsAuthenticated` + `IsAdministrador`)
- **Paginación:** Sí, usando `PetTechPagination` (page_size=20)
- **Filtros query params:**
  - `?especie=PERRO|GATO|CONEJO`
  - `?estado_calendario=al_dia|con_vencidas|completado`

### Response body (paginado)
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "adopcion_id": 2,
      "fecha_adopcion": "2026-03-26",
      "mascota_id": 5,
      "mascota_nombre": "Luna",
      "mascota_especie": "PERRO",
      "mascota_raza": "Labrador",
      "mascota_foto_url": "https://res.cloudinary.com/...",
      "familia_nombre": "Familia García",
      "total_vacunas": 8,
      "vacunas_completadas": 5,
      "vacunas_vencidas": 1,
      "estado_calendario": "con_vencidas"
    }
  ]
}
```

### Lógica de `estado_calendario`
- `completado`: todas las entradas tienen `completada=True`
- `con_vencidas`: al menos una entrada tiene `completada=False` y `fecha_sugerida < hoy`
- `al_dia`: ninguna vencida y al menos una pendiente

## Cambios requeridos

### 1. Nuevo serializer: `ResumenCalendarioSerializer`
En `apps/adopciones/interfaces/serializers.py` — campos calculados (`vacunas_completadas`, `vacunas_vencidas`, `estado_calendario`) como `SerializerMethodField`.

### 2. Nueva vista: `CalendariosAdminListView`
En `apps/adopciones/interfaces/views.py` — `GET /api/v1/calendarios/`, solo ADMIN.

### 3. Nueva URL
En `apps/adopciones/interfaces/urls.py`:
```python
path('calendarios/', CalendariosAdminListView.as_view(), name='calendarios-list'),
```

## Criterios de Aceptación (Alto Nivel)

1. `GET /api/v1/calendarios/` con token ADMIN → HTTP 200 con lista paginada.
2. `GET /api/v1/calendarios/` con token FAMILIA → HTTP 403.
3. `GET /api/v1/calendarios/` sin token → HTTP 401.
4. `?especie=PERRO` filtra correctamente los resultados.
5. `?estado_calendario=con_vencidas` solo devuelve calendarios con al menos una vacuna vencida.
6. Los campos calculados (`vacunas_completadas`, `vacunas_vencidas`, `estado_calendario`) son correctos según los datos reales de `EntradaCalendario`.
7. La paginación funciona correctamente con `page` y `page_size`.
