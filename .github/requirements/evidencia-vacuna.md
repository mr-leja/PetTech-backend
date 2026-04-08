# Requerimiento: Evidencia fotográfica de vacuna aplicada (Backend)

## Descripción General

El backend ya expone el endpoint `PATCH /api/v1/entradas/<entrada_id>/aplicar/` que recibe `foto_comprobante` como `multipart/form-data` y marca la `EntradaCalendario` como `completada=True`. Sin embargo, presenta las siguientes deficiencias:

1. **Sin validación de archivo:** No se valida tipo MIME ni tamaño máximo en el serializer ni en la vista.
2. **Sin campo de fecha de aplicación real:** La entrada se marca como completada pero no registra la fecha exacta en que fue aplicada la vacuna.
3. **El ADMIN no puede marcar vacunas:** El endpoint solo permite que la familia (dueña de la adopción) marque vacunas; falta control de acceso para que el ADMIN también pueda hacerlo.

## Solución Propuesta

### 1. Validación de archivo en `MarcarVacunaAplicadaSerializer`
```python
def validate_foto_comprobante(self, value):
    tipos_permitidos = ['image/jpeg', 'image/png', 'image/webp']
    if value.content_type not in tipos_permitidos:
        raise serializers.ValidationError('Solo se permiten imágenes JPG, PNG o WEBP.')
    if value.size > 5 * 1024 * 1024:
        raise serializers.ValidationError('La imagen no puede superar 5 MB.')
    return value
```

### 2. Campo `fecha_aplicacion` en `EntradaCalendario`
- Agregar campo `fecha_aplicacion = models.DateField(null=True, blank=True)` al modelo.
- Al marcar como aplicada, registrar `fecha_aplicacion = date.today()`.
- Exponer el campo en `EntradaCalendarioSerializer`.

### 3. Control de acceso en `MarcarVacunaAplicadaView`
- ADMIN: puede marcar cualquier entrada de cualquier adopción.
- FAMILIA: solo puede marcar entradas de sus propias adopciones (validación existente).

## Criterios de Aceptación (Alto Nivel)

1. `PATCH /api/v1/entradas/<id>/aplicar/` con archivo no imagen → HTTP 400 con mensaje en español.
2. `PATCH /api/v1/entradas/<id>/aplicar/` con archivo > 5 MB → HTTP 400 con mensaje en español.
3. Al marcar como aplicada, el campo `fecha_aplicacion` queda registrado con la fecha actual.
4. El ADMIN puede marcar como aplicada cualquier entrada → HTTP 200.
5. La FAMILIA solo puede marcar entradas de sus propias adopciones → HTTP 403 si intenta acceder a otra.
6. La migración de `fecha_aplicacion` es compatible con registros existentes (`null=True`).
