---
id: SPEC-004
status: IMPLEMENTED
feature: calendario-admin
created: 2026-04-08
updated: 2026-04-08
author: spec-generator
version: "1.0"
related-specs: [SPEC-003]
---

# Spec: Endpoint de Listado de Calendarios para el Administrador (Backend)

> **Estado:** `DRAFT` → aprobar con `status: APPROVED` antes de iniciar implementación.
> **Ciclo de vida:** DRAFT → APPROVED → IN_PROGRESS → IMPLEMENTED → DEPRECATED

---

## 1. REQUERIMIENTOS

### Descripción

Nuevo endpoint `GET /api/v1/calendarios/` exclusivo para ADMIN. Devuelve el listado paginado de todos los `CalendarioVacunacion` con un resumen calculado por cada uno (vacunas completadas, vencidas, estado del calendario) y los datos de mascota y familia relacionados.

Fuente: `MVP_PetTech/.github/requirements/calendario-admin.md`

### Historias de Usuario

#### HU-20: Exponer listado de calendarios con resumen para el ADMIN

```
Como:        Administrador
Quiero:      llamar a GET /api/v1/calendarios/ y recibir listado paginado con resumen
Para:        alimentar la vista de control de calendarios de vacunación

Prioridad:   Alta
Estimación:  S
Dependencias: CalendarioVacunacion, EntradaCalendario, Adopcion, Mascota, Familia ya existen
Capa:        Backend
```

**Happy Path**
```gherkin
CRITERIO-20.1: Listado exitoso
  Dado que:  se hace GET /api/v1/calendarios/ con token ADMIN
  Entonces:  retorna HTTP 200 con lista paginada de ResumenCalendario
  Y:         cada item tiene los campos de mascota, familia y resumen calculado

CRITERIO-20.4: Control de acceso
  Dado que:  se hace GET /api/v1/calendarios/ con token FAMILIA
  Entonces:  retorna HTTP 403

  Dado que:  se hace GET /api/v1/calendarios/ sin token
  Entonces:  retorna HTTP 401
```

#### HU-21: Filtrar por especie y estado

```gherkin
CRITERIO-21.1: Filtro por especie
  Dado que:  GET /api/v1/calendarios/?especie=PERRO con token ADMIN
  Entonces:  solo se retornan calendarios donde mascota.especie == 'PERRO'

CRITERIO-21.2: Filtro por estado_calendario
  Dado que:  GET /api/v1/calendarios/?estado_calendario=con_vencidas
  Entonces:  solo se retornan calendarios con al menos una vacuna vencida hoy
```

### Reglas de Negocio

| ID | Regla |
|---|---|
| RN-01 | Solo ADMIN puede acceder al endpoint |
| RN-02 | `estado_calendario=completado`: todas las entradas tienen `completada=True` |
| RN-03 | `estado_calendario=con_vencidas`: ≥1 entrada con `completada=False` y `fecha_sugerida < hoy` |
| RN-04 | `estado_calendario=al_dia`: sin vencidas y al menos una entrada `completada=False` |
| RN-05 | Paginación con `PetTechPagination` (page_size=20, max=100) |
| RN-06 | `vacunas_vencidas` se calcula sobre entradas con `completada=False` y `fecha_sugerida < date.today()` |

---

## 2. DISEÑO

### 2.1 Nuevo serializer

**Archivo:** `apps/adopciones/interfaces/serializers.py`

```python
class ResumenCalendarioSerializer(serializers.ModelSerializer):
    adopcion_id         = serializers.IntegerField(source='adopcion.id', read_only=True)
    fecha_adopcion      = serializers.DateTimeField(source='adopcion.fecha_adopcion', read_only=True)
    mascota_id          = serializers.IntegerField(source='adopcion.solicitud.mascota.id', read_only=True)
    mascota_nombre      = serializers.CharField(source='adopcion.solicitud.mascota.nombre', read_only=True)
    mascota_especie     = serializers.CharField(source='adopcion.solicitud.mascota.especie', read_only=True)
    mascota_raza        = serializers.CharField(source='adopcion.solicitud.mascota.raza', read_only=True)
    mascota_foto_url    = serializers.SerializerMethodField()
    familia_nombre      = serializers.CharField(source='adopcion.solicitud.familia.nombre_familia', read_only=True)
    total_vacunas       = serializers.SerializerMethodField()
    vacunas_completadas = serializers.SerializerMethodField()
    vacunas_vencidas    = serializers.SerializerMethodField()
    estado_calendario   = serializers.SerializerMethodField()

    class Meta:
        model = CalendarioVacunacion
        fields = [
            'id', 'adopcion_id', 'fecha_adopcion',
            'mascota_id', 'mascota_nombre', 'mascota_especie', 'mascota_raza', 'mascota_foto_url',
            'familia_nombre',
            'total_vacunas', 'vacunas_completadas', 'vacunas_vencidas', 'estado_calendario',
        ]

    def get_mascota_foto_url(self, obj):
        request = self.context.get('request')
        mascota = obj.adopcion.solicitud.mascota
        if mascota.foto:
            return request.build_absolute_uri(mascota.foto.url) if request else mascota.foto.url
        return None

    def get_total_vacunas(self, obj):
        return obj.entradas.count()

    def get_vacunas_completadas(self, obj):
        return obj.entradas.filter(completada=True).count()

    def get_vacunas_vencidas(self, obj):
        from datetime import date
        return obj.entradas.filter(completada=False, fecha_sugerida__lt=date.today()).count()

    def get_estado_calendario(self, obj):
        from datetime import date
        total = obj.entradas.count()
        completadas = obj.entradas.filter(completada=True).count()
        if completadas == total:
            return 'completado'
        vencidas = obj.entradas.filter(completada=False, fecha_sugerida__lt=date.today()).count()
        if vencidas > 0:
            return 'con_vencidas'
        return 'al_dia'
```

### 2.2 Nueva vista

**Archivo:** `apps/adopciones/interfaces/views.py`

```python
class CalendariosAdminListView(APIView):
    """
    GET /api/v1/calendarios/ — Solo ADMIN.
    Lista todos los CalendarioVacunacion con resumen calculado.
    Filtros: ?especie= ?estado_calendario=
    """
    permission_classes = [IsAuthenticated, IsAdministrador]

    def get(self, request):
        from apps.adopciones.infrastructure.models import CalendarioVacunacion
        from datetime import date

        qs = CalendarioVacunacion.objects.select_related(
            'adopcion__solicitud__mascota',
            'adopcion__solicitud__familia',
        ).prefetch_related('entradas')

        especie = request.query_params.get('especie')
        if especie:
            qs = qs.filter(adopcion__solicitud__mascota__especie=especie)

        estado_calendario = request.query_params.get('estado_calendario')
        if estado_calendario:
            if estado_calendario == 'completado':
                # Todos los entradas completadas
                qs = [c for c in qs if c.entradas.filter(completada=False).count() == 0 and c.entradas.count() > 0]
            elif estado_calendario == 'con_vencidas':
                qs = [c for c in qs if c.entradas.filter(completada=False, fecha_sugerida__lt=date.today()).exists()]
            elif estado_calendario == 'al_dia':
                qs = [c for c in qs if
                      not c.entradas.filter(completada=False, fecha_sugerida__lt=date.today()).exists()
                      and c.entradas.filter(completada=False).exists()]

        paginator = PetTechPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ResumenCalendarioSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
```

### 2.3 Nueva URL

**Archivo:** `apps/adopciones/interfaces/urls.py`

```python
path('calendarios/', CalendariosAdminListView.as_view(), name='calendarios-list'),
```

### 2.4 Contrato API

**`GET /api/v1/calendarios/`**

| Query param | Tipo | Valores |
|---|---|---|
| `especie` | string (opcional) | `PERRO`, `GATO`, `CONEJO` |
| `estado_calendario` | string (opcional) | `al_dia`, `con_vencidas`, `completado` |
| `page` | int (opcional) | número de página |
| `page_size` | int (opcional) | máx 100 |

**Response 200:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "adopcion_id": 2,
      "fecha_adopcion": "2026-03-26T10:00:00Z",
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

**Códigos HTTP:**
| Código | Situación |
|---|---|
| 200 | Listado retornado |
| 401 | Sin autenticación |
| 403 | Rol no es ADMIN |

---

## 3. LISTA DE TAREAS

### Backend

- [ ] Agregar `ResumenCalendarioSerializer` en `serializers.py`
- [ ] Agregar `CalendariosAdminListView` en `views.py`
- [ ] Registrar `path('calendarios/', ...)` en `urls.py`
- [ ] Importar y usar `PetTechPagination` en la nueva vista
- [ ] Importar `ResumenCalendarioSerializer` en la vista
- [ ] Verificar que `select_related` y `prefetch_related` evitan N+1 queries
- [ ] Agregar import de `CalendarioVacunacion` en la vista si no está disponible via repositorio

### QA

- [ ] GET /api/v1/calendarios/ con ADMIN → HTTP 200, lista paginada
- [ ] GET /api/v1/calendarios/ con FAMILIA → HTTP 403
- [ ] GET /api/v1/calendarios/ sin token → HTTP 401
- [ ] ?especie=GATO → solo calendarios de gatos
- [ ] ?estado_calendario=completado → solo calendarios con todas las vacunas aplicadas
- [ ] ?estado_calendario=con_vencidas → solo calendarios con ≥1 vencida
- [ ] ?estado_calendario=al_dia → no tiene vencidas, tiene pendientes
- [ ] `vacunas_vencidas` calculado correctamente según fecha de hoy
- [ ] `estado_calendario` consistente con `vacunas_completadas` y `vacunas_vencidas`
- [ ] Paginación funciona con `?page=2`
