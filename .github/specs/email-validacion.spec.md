---
id: SPEC-001
status: IMPLEMENTED
feature: email-validacion
created: 2026-03-30
updated: 2026-03-30
author: spec-generator
version: "1.1"
related-specs: []
---

# Spec: Validaciones de Correo y Contraseña

> **Estado:** `DRAFT` → aprobar con `status: APPROVED` antes de iniciar implementación.
> **Ciclo de vida:** DRAFT → APPROVED → IN_PROGRESS → IMPLEMENTED → DEPRECATED

---

## 1. REQUERIMIENTOS

### Descripción

Esta funcionalidad estandariza y refuerza las validaciones de los campos `email` y `password` en los puntos de entrada del sistema PetTech: el serializer DRF (backend) y los schemas Zod (frontend). El objetivo es garantizar mensajes de error consistentes en español, normalización del correo, y una política de contraseña robusta y consistente entre todos los formularios.

### Requerimiento de Negocio

Fuente principal: `.github/requirements/email-validacion.md`.

Resumen:
- Validaciones de email robustas en `RegistroSerializer` y `UsuarioSerializer` (DRF).
- Mensaje en español para email duplicado: `'Este correo ya está registrado.'`
- Schemas Zod en `RegisterPage.tsx` y `LoginPage.tsx` con mensajes en español, límites de longitud y `.trim()` en email.
- El campo email se normaliza (trim + lowercase) antes de enviarse al backend.
- **Contraseña:** mínimo 8 caracteres en todos los formularios (registro y login). En el **registro** además debe cumplir: al menos 1 letra + 1 número + 1 carácter especial.

### Historias de Usuario

#### HU-01: Mostrar error claro al registrar un correo inválido o duplicado

```
Como:        Usuario que completa el formulario de registro
Quiero:      ver un mensaje de error claro si mi correo es inválido o ya está registrado
Para:        saber qué corregir sin ambigüedad

Prioridad:   Media
Estimación:  S
Dependencias: Ninguna
Capa:        Backend + Frontend
```

#### Criterios de Aceptación — HU-01

**Happy Path**
```gherkin
CRITERIO-1.1: Registro con correo válido y único
  Dado que:  el Usuario está en el formulario de registro (paso 1)
  Cuando:    ingresa un correo con formato válido y que no existe en el sistema
  Entonces:  el formulario no muestra errores en el campo email
  Y:         el backend acepta el registro con HTTP 201
```

**Error Path**
```gherkin
CRITERIO-1.2: Correo con formato inválido (frontend)
  Dado que:  el Usuario está en el formulario de registro
  Cuando:    ingresa un valor sin '@' o sin dominio en el campo correo
  Entonces:  el schema Zod muestra 'Ingresa un correo electrónico válido.'
  Y:         el formulario no envía la solicitud al backend

CRITERIO-1.3: Correo ya registrado (backend)
  Dado que:  ya existe un Usuario con ese correo en la base de datos
  Cuando:    el Usuario intenta registrarse con el mismo correo
  Entonces:  el backend retorna HTTP 400
  Y:         la respuesta contiene el campo email con el mensaje 'Este correo ya está registrado.'

CRITERIO-1.4: Correo vacío
  Dado que:  el Usuario está en el formulario de registro o login
  Cuando:    deja el campo correo vacío y envía el formulario
  Entonces:  el schema Zod muestra 'El correo es obligatorio.'
  Y:         el formulario no envía la solicitud al backend
```

**Edge Cases**
```gherkin
CRITERIO-1.5: Correo con espacios al inicio o al final
  Dado que:  el Usuario ingresa '  user@example.com  ' con espacios
  Cuando:    el formulario procesa el valor
  Entonces:  el valor es recortado con .trim() antes de enviarse al backend
  Y:         el backend normaliza el email a minúsculas antes de guardarlo

CRITERIO-1.6: Correo que supera 254 caracteres
  Dado que:  el Usuario ingresa un correo con más de 254 caracteres
  Cuando:    el schema Zod valida el campo
  Entonces:  muestra 'El correo no puede superar 254 caracteres.'
  Y:         el formulario no envía la solicitud al backend
```

#### HU-02: Mostrar error claro al iniciar sesión con correo inválido

```
Como:        Usuario que intenta iniciar sesión
Quiero:      ver un mensaje de error inmediato si mi correo tiene formato inválido
Para:        corregirlo antes de enviar la solicitud al servidor

Prioridad:   Media
Estimación:  XS
Dependencias: Ninguna
Capa:        Frontend
```

#### Criterios de Aceptación — HU-02

**Error Path**
```gherkin
CRITERIO-2.1: Correo inválido en login (frontend)
  Dado que:  el Usuario está en el formulario de login
  Cuando:    ingresa un valor sin formato de correo y pierde el foco del campo
  Entonces:  el schema Zod muestra 'Ingresa un correo electrónico válido.'
  Y:         el botón de envío no ejecuta la petición HTTP

CRITERIO-2.2: Correo vacío en login
  Dado que:  el Usuario está en el formulario de login
  Cuando:    deja el campo correo vacío y hace clic en 'Ingresar'
  Entonces:  react-hook-form muestra 'El correo es obligatorio.'
```

#### HU-03: Validar complejidad de contraseña en el registro

```
Como:        Usuario que se registra en PetTech
Quiero:      recibir un error claro si mi contraseña no cumple los requisitos de complejidad
Para:        crear una cuenta con una contraseña segura desde el primer intento

Prioridad:   Media
Estimación:  S
Dependencias: Ninguna
Capa:        Backend + Frontend
```

#### Criterios de Aceptación — HU-03

**Happy Path**
```gherkin
CRITERIO-3.1: Contraseña válida en registro
  Dado que:  el Usuario está en el formulario de registro (paso 1)
  Cuando:    ingresa una contraseña como 'MiClave1!' (8+ chars, letra, número, especial)
  Entonces:  el schema Zod no muestra errores en el campo contraseña
  Y:         el backend acepta el registro con HTTP 201
```

**Error Path**
```gherkin
CRITERIO-3.2: Contraseña sin carácter especial
  Dado que:  el Usuario está en el formulario de registro
  Cuando:    ingresa 'MiClave1' (sin carácter especial)
  Entonces:  el schema Zod muestra 'La contraseña debe incluir al menos una letra, un número y un carácter especial.'

CRITERIO-3.3: Contraseña sin número
  Dado que:  el Usuario está en el formulario de registro
  Cuando:    ingresa 'MiClave!' (sin número)
  Entonces:  el schema Zod muestra 'La contraseña debe incluir al menos una letra, un número y un carácter especial.'

CRITERIO-3.4: Contraseña de menos de 8 caracteres
  Dado que:  el Usuario está en el formulario de registro o login
  Cuando:    ingresa una contraseña con menos de 8 caracteres
  Entonces:  el schema Zod muestra 'Mínimo 8 caracteres.'

CRITERIO-3.5: Contraseña de menos de 8 caracteres en login
  Dado que:  el Usuario está en el formulario de login
  Cuando:    ingresa menos de 8 caracteres en el campo contraseña
  Entonces:  el schema Zod muestra 'Mínimo 8 caracteres.'
  Y:         NO se verifica complejidad (el usuario ya tiene su contraseña establecida)
```

**Edge Case**
```gherkin
CRITERIO-3.6: Contraseña solo de números
  Dado que:  el Usuario está en el formulario de registro
  Cuando:    ingresa '12345678' (solo números, sin letra ni especial)
  Entonces:  el schema Zod muestra el mensaje de complejidad
```

### Reglas de Negocio

1. El campo `email` es el identificador único del `Usuario`. Toda validación debe aplicarse antes de cualquier operación de escritura en PostgreSQL.
2. El email se normaliza a minúsculas antes de la comparación de unicidad.
3. Mensajes de error del campo `email` deben estar siempre en español.
4. La longitud máxima de email es 254 caracteres (RFC 5321). Esta regla aplica tanto en DRF como en Zod.
5. Los formularios usan validación on-blur para el campo email (react-hook-form `mode: 'onBlur'`).
6. La contraseña debe tener mínimo **8 caracteres** en todos los formularios (registro y login).
7. En el **registro**, la contraseña debe contener al menos: 1 letra `[A-Za-z]`, 1 número `[0-9]` y 1 carácter especial `[!@#$%^&*...]`.
8. En el **login**, solo se valida longitud mínima (8 chars) — no se verifica complejidad.
9. El mensaje único de complejidad de contraseña es: `'La contraseña debe incluir al menos una letra, un número y un carácter especial.'`

---

## 2. DISEÑO

### Modelos de Datos

No se requieren cambios en el modelo `Usuario` ni en las migraciones. Las validaciones van exclusivamente en el serializer y en los schemas Zod.

| Capa | Archivo | Cambio |
|------|---------|--------|
| Backend serializer | `apps/usuarios/interfaces/serializers.py` | Agregar `validate_email()` en `RegistroSerializer` y `UsuarioSerializer`; agregar `validate_password()` en `RegistroSerializer` |
| Frontend schema | `features/auth/pages/RegisterPage.tsx` | Extender `step1Schema.email` y `step1Schema.password` con reglas de complejidad |
| Frontend schema | `features/auth/pages/LoginPage.tsx` | Extender `schema.email` y `schema.password` (solo `min(8)`, sin complejidad) |

### API — Cambios en Respuestas de Error

No se agregan endpoints nuevos. Se modifica la forma en que `RegistroSerializer` reporta errores de validación del campo `email`.

#### POST /api/v1/usuarios/registro/ — errores de email

**Antes (Django genérico):**
```json
{
  "email": ["Ya existe usuario con este/a Email."]
}
```

**Después (mensajes en español amigables):**
```json
{
  "email": ["Este correo ya está registrado."]
}
```

**Email inválido (sin cambio de estructura, mejora de mensaje):**
```json
{
  "email": ["Ingresa un correo electrónico válido."]
}
```

### Diseño Frontend

#### Schema Zod unificado para email

```typescript
// Patrón único para campo email en todos los formularios
const emailField = z
  .string({ required_error: 'El correo es obligatorio.' })
  .trim()
  .min(5, 'El correo es demasiado corto.')
  .max(254, 'El correo no puede superar 254 caracteres.')
  .email('Ingresa un correo electrónico válido.');
```

#### Schema Zod para contraseña en registro

```typescript
// Solo para RegisterPage — incluye regla de complejidad
const PASSWORD_REGEX = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?])/;

const passwordField = z
  .string({ required_error: 'La contraseña es obligatoria.' })
  .min(8, 'Mínimo 8 caracteres.')
  .regex(PASSWORD_REGEX, 'La contraseña debe incluir al menos una letra, un número y un carácter especial.');
```

#### Schema Zod para contraseña en login

```typescript
// Solo para LoginPage — solo longitud mínima, sin complejidad
const passwordLoginField = z
  .string({ required_error: 'La contraseña es obligatoria.' })
  .min(8, 'Mínimo 8 caracteres.');
```

### Diseño Backend

#### `validate_email` en `RegistroSerializer`

```python
# apps/usuarios/interfaces/serializers.py
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

class RegistroSerializer(serializers.ModelSerializer):
    # ...
    def validate_email(self, value: str) -> str:
        value = value.strip().lower()
        try:
            django_validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError('Ingresa un correo electrónico válido.')
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este correo ya está registrado.')
        return value
```

#### `validate_password` en `RegistroSerializer`

```python
import re

PASSWORD_REGEX = re.compile(
    r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':"|,.<>\/?])'
)

class RegistroSerializer(serializers.ModelSerializer):
    # ...
    def validate_password(self, value: str) -> str:
        if not PASSWORD_REGEX.search(value):
            raise serializers.ValidationError(
                'La contraseña debe incluir al menos una letra, un número y un carácter especial.'
            )
        return value
```

> El campo `password` ya tiene `min_length=8` — no se modifica ese declarativo.

---

## 3. LISTA DE TAREAS

### Backend

- [x] Agregar método `validate_email()` en `RegistroSerializer` con normalización (trim + lower), validación de formato y mensaje de unicidad en español.
- [x] Agregar método `validate_email()` en `UsuarioSerializer` para el endpoint de actualización de perfil.
- [x] Verificar que `core/exception_handler.py` no sobreescriba los mensajes de validación de campo.
- [x] Agregar método `validate_password()` en `RegistroSerializer` con regex de complejidad (letra + número + carácter especial) y mensaje en español.

### Frontend

- [x] Definir el patrón de email field Zod en `RegisterPage.tsx` → `step1Schema`.
- [x] Definir el patrón de email field Zod en `LoginPage.tsx` → `schema`.
- [x] Agregar `mode: 'onBlur'` en `useForm` de `LoginPage.tsx` y `RegisterPage.tsx`.
- [x] Agregar regex de complejidad al campo `password` en `step1Schema` (`RegisterPage.tsx`).
- [x] Actualizar `schema.password` en `LoginPage.tsx` a `min(8)` (era `min(6)`).

### QA

- [x] Test unitario backend: `test_registro_email_invalido` → 400 con mensaje en español.
- [x] Test unitario backend: `test_registro_email_duplicado` → 400 con `'Este correo ya está registrado.'`
- [x] Test unitario backend: `test_registro_email_normalizado` → guardado en minúsculas y sin espacios.
- [x] Test unitario frontend: `LoginPage` muestra error Zod al ingresar correo sin `@`.
- [x] Test unitario frontend: `RegisterPage` (paso 1) muestra error al superar 254 chars en email.
- [x] Test unitario backend: `test_registro_password_sin_especial` → 400 con mensaje de complejidad.
- [x] Test unitario backend: `test_registro_password_sin_numero` → 400 con mensaje de complejidad.
- [x] Test unitario frontend: `RegisterPage` muestra error de complejidad al ingresar 'Abcdefgh' (sin especial).
- [x] Test unitario frontend: `LoginPage` muestra error al ingresar contraseña de 7 caracteres.
