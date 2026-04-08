---
id: SPEC-003
status: IMPLEMENTED
feature: evidencia-vacuna
created: 2026-04-08
updated: 2026-04-08
author: spec-generator
version: "1.0"
related-specs: [SPEC-001]
---

# Spec: Evidencia fotográfica de vacuna aplicada

> **Estado:** `DRAFT` → aprobar con `status: APPROVED` antes de iniciar implementación.
> **Ciclo de vida:** DRAFT → APPROVED → IN_PROGRESS → IMPLEMENTED → DEPRECATED

---

## 1. REQUERIMIENTOS

### Descripción

Mejoras al endpoint `PATCH /api/v1/entradas/<entrada_id>/aplicar/`:
- Validación de tipo MIME y tamaño del archivo adjunto.
- Registro del campo `fecha_aplicacion` en `EntradaCalendario`.
- Control de acceso extendido: el ADMIN también puede marcar vacunas.

Fuente: `MVP_PetTech/.github/requirements/evidencia-vacuna.md`

### Historias de Usuario

#### HU-16: Validar archivo de comprobante en el backend

```
Como:        Sistema backend de PetTech
Quiero:      rechazar archivos con tipo MIME no permitido o tamaño excesivo
Para:        garantizar la integridad y seguridad del almacenamiento de imágenes

Prioridad:   Alta
Estimación:  XS
Capa:        Backend
```

```gherkin
CRITERIO-16.4: Tipo MIME inválido
  Dado que:  se envía PATCH /api/v1/entradas/<id>/aplicar/ con foto_comprobante = archivo PDF
  Cuando:    el serializer ejecuta validate_foto_comprobante
  Entonces:  retorna HTTP 400
  Y:         body contiene {"foto_comprobante": "Solo se permiten imágenes JPG, PNG o WEBP."}

CRITERIO-16.5: Tamaño excesivo
  Dado que:  se envía un archivo de 6 MB
  Cuando:    el serializer ejecuta validate_foto_comprobante
  Entonces:  retorna HTTP 400
  Y:         body contiene {"foto_comprobante": "La imagen no puede superar 5 MB."}

CRITERIO-16.1: Archivo válido aceptado
  Dado que:  se envía una imagen JPEG de 1 MB con token válido
  Entonces:  retorna HTTP 200 con la EntradaCalendario actualizada
```

#### HU-17: Registrar fecha de aplicación de vacuna

```
Como:        Administrador del sistema
Quiero:      que se registre la fecha en que se marcó una vacuna como aplicada
Para:        tener trazabilidad precisa del historial de vacunación

Prioridad:   Media
Estimación:  XS
Capa:        Backend
```

```gherkin
CRITERIO-17.1: Fecha registrada automáticamente
  Dado que:  PATCH /api/v1/entradas/<id>/aplicar/ es exitoso
  Entonces:  EntradaCalendario.fecha_aplicacion == date.today()
  Y:         la response incluye "fecha_aplicacion": "YYYY-MM-DD"

CRITERIO-17.2: Compatibilidad con registros existentes
  Dado que:  existen EntradaCalendario sin fecha_aplicacion antes de la migración
  Entonces:  esas entradas tienen fecha_aplicacion = null (no rompe la migración)
```

#### HU-19: El ADMIN puede marcar vacunas como aplicadas

```
Como:        Administrador
Quiero:      poder llamar a PATCH /api/v1/entradas/<id>/aplicar/ sin restricción de familia
Para:        registrar vacunas aplicadas en clínica directamente

Prioridad:   Baja
Estimación:  XS
Capa:        Backend
```

```gherkin
CRITERIO-19.2: ADMIN tiene acceso de escritura completo
  Dado que:  se hace PATCH /api/v1/entradas/<id>/aplicar/ con token ADMIN
  Entonces:  el backend no valida familia propietaria
  Y:         retorna HTTP 200

CRITERIO-19.3: FAMILIA intenta acceso ajeno
  Dado que:  FAMILIA intenta marcar vacuna de adopción de otra familia
  Entonces:  el backend retorna HTTP 403
```

### Reglas de Negocio

| ID | Regla |
|---|---|
| RN-01 | Tipos permitidos: `image/jpeg`, `image/png`, `image/webp` |
| RN-02 | Tamaño máximo: 5 MB (5 * 1024 * 1024 bytes) |
| RN-03 | `fecha_aplicacion` se registra con `date.today()` en timezone del servidor |
| RN-04 | ADMIN puede operar sobre cualquier entrada |
| RN-05 | FAMILIA solo puede operar sobre entradas de sus propias adopciones |

---

## 2. DISEÑO

### 2.1 Cambio de modelo

**Archivo:** `apps/adopciones/infrastructure/models.py`

```python
class EntradaCalendario(models.Model):
    ...
    # NUEVO
    fecha_aplicacion = models.DateField(null=True, blank=True)
```

### 2.2 Migración

```
apps/adopciones/migrations/0006_entradacalendario_fecha_aplicacion.py
```

Generada con `python manage.py makemigrations adopciones`.

### 2.3 Serializer

**Archivo:** `apps/adopciones/interfaces/serializers.py`

`EntradaCalendarioSerializer` — agregar campo:
```python
fecha_aplicacion = serializers.DateField(read_only=True, allow_null=True)
```

`MarcarVacunaAplicadaSerializer` — agregar método:
```python
def validate_foto_comprobante(self, value):
    tipos_permitidos = ['image/jpeg', 'image/png', 'image/webp']
    if value.content_type not in tipos_permitidos:
        raise serializers.ValidationError('Solo se permiten imágenes JPG, PNG o WEBP.')
    if value.size > 5 * 1024 * 1024:
        raise serializers.ValidationError('La imagen no puede superar 5 MB.')
    return value
```

### 2.4 Vista

**Archivo:** `apps/adopciones/interfaces/views.py`

`MarcarVacunaAplicadaView.patch` — lógica actualizada:

```python
def patch(self, request, entrada_id):
    entrada = calendario_repo.obtener_entrada(entrada_id)
    if not entrada:
        return Response({'error': 'Vacuna no encontrada.'}, status=404)

    user = request.user
    if user.rol != 'ADMIN':
        # Validar familia propietaria (lógica existente)
        try:
            familia = user.familia
            if entrada.calendario.adopcion.solicitud.familia_id != familia.id:
                return Response({'error': 'No tienes permiso para modificar esta entrada.'}, status=403)
        except Exception:
            return Response(status=403)

    serializer = MarcarVacunaAplicadaSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    # Guardar foto + marcar completada + fecha
    entrada.foto_comprobante = serializer.validated_data['foto_comprobante']
    entrada.completada = True
    entrada.fecha_aplicacion = date.today()
    entrada.save()

    return Response(EntradaCalendarioSerializer(entrada, context={'request': request}).data)
```

### 2.5 Contrato API actualizado

**`PATCH /api/v1/entradas/<entrada_id>/aplicar/`**

| Campo | Tipo | Requerido |
|---|---|---|
| `foto_comprobante` | `File (image/jpeg\|png\|webp, ≤5MB)` | Sí |

**Response 200:**
```json
{
  "id": 3,
  "nombre_vacuna": "Rabia",
  "descripcion": "Antirrábica anual",
  "fecha_sugerida": "2026-04-15",
  "es_refuerzo": false,
  "completada": true,
  "fecha_aplicacion": "2026-04-08",
  "foto_comprobante_url": "https://res.cloudinary.com/..."
}
```

**Response 400:**
```json
{"foto_comprobante": "Solo se permiten imágenes JPG, PNG o WEBP."}
```

**Códigos HTTP:**
| Código | Situación |
|---|---|
| 200 | Vacuna marcada exitosamente |
| 400 | Archivo inválido (tipo o tamaño) |
| 401 | Sin autenticación |
| 403 | FAMILIA intenta acceder a entrada ajena |
| 404 | Entrada no encontrada |

---

## 3. LISTA DE TAREAS

### Backend

- [ ] Agregar `fecha_aplicacion = DateField(null=True, blank=True)` a `EntradaCalendario`
- [ ] Ejecutar `makemigrations` y verificar migración generada
- [ ] Agregar `fecha_aplicacion` a `EntradaCalendarioSerializer` (read_only)
- [ ] Agregar `validate_foto_comprobante` en `MarcarVacunaAplicadaSerializer`
- [ ] Actualizar lógica de `MarcarVacunaAplicadaView`: acceso ADMIN + registro `fecha_aplicacion`
- [ ] Actualizar `CalendarioRepository.obtener_entrada()` si es necesario

### QA

- [ ] PATCH con JPG válido (FAMILIA propietaria) → HTTP 200, `completada=true`, `fecha_aplicacion` presente
- [ ] PATCH con PDF → HTTP 400, mensaje en español
- [ ] PATCH con imagen > 5 MB → HTTP 400, mensaje en español
- [ ] PATCH con token ADMIN cualquier entrada → HTTP 200
- [ ] PATCH con FAMILIA sobre entrada ajena → HTTP 403
- [ ] Verificar que `fecha_aplicacion=null` en entradas sin aplicar (no rompe serializer)
- [ ] Verificar migración no rompe entradas existentes
