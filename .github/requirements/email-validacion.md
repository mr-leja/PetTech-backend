# Requerimiento: Validaciones de Correo y Contraseña

## Descripción General

El campo `email` es el identificador principal del `Usuario` en PetTech (es el `USERNAME_FIELD`). Actualmente las validaciones de este campo son básicas tanto en el backend como en el frontend. Además, existe una **inconsistencia** en la validación del campo `password`: el formulario de registro exige mínimo 8 caracteres pero el de login solo exige 6, y ninguno verifica complejidad. Se requiere una validación consistente, robusta y con mensajes de error claros en español en todos los formularios.

## Problema / Necesidad

1. **Inconsistencia entre capas (email):** El frontend valida el email con Zod pero el backend no devuelve los mismos mensajes de error ni aplica las mismas reglas.
2. **Mensajes de error incompletos:** Si se intenta registrar un email ya existente, el backend retorna un error genérico de Django que no es amigable para el usuario.
3. **Sin límite de longitud explícito en email:** El campo `email` no tiene un límite máximo explícito en el serializer DRF.
4. **Sin normalización garantizada en el serializer:** El email debe ser normalizado a minúsculas antes de guardarse.
5. **Inconsistencia en contraseña:** El schema de registro exige `min(8)` pero el de login exige `min(6)`. Ambos deben exigir mínimo 8 caracteres.
6. **Sin regla de complejidad en contraseña:** No se verifica que la contraseña incluya al menos una letra, un número y un carácter especial.

## Solución Propuesta

### 1. Backend — `RegistroSerializer` y `UsuarioSerializer` (Django DRF)

Mejorar las validaciones del campo `email` en los serializers del módulo `apps/usuarios/interfaces/serializers.py`:

- **Formato RFC 5322:** Usar `django.core.validators.validate_email` explícitamente en el método `validate_email()` del serializer para mensajes de error en español.
- **Longitud máxima:** Limitar el email a 254 caracteres (RFC 5321) con mensaje de error claro.
- **Unicidad con mensaje amigable:** El error de email duplicado debe retornar HTTP 400 con el mensaje: `'Este correo ya está registrado.'` en lugar del mensaje genérico de Django.
- **Normalización:** El serializer debe normalizar el email a minúsculas antes de la validación de unicidad.

### 2. Backend — `RegistroSerializer` (campo `password`)

Agregar validación de complejidad en el `RegistroSerializer`:

- **Longitud mínima:** 8 caracteres (ya existe `min_length=8` en el campo; mantener).
- **Complejidad:** La contraseña debe contener al menos una letra, un número y un carácter especial (ej. `!@#$%^&*`). Validar con `validate_password()` en el método `validate_password()`.
- **Mensaje de error claro:** `'La contraseña debe tener mínimo 8 caracteres e incluir al menos una letra, un número y un carácter especial.'`

### 3. Frontend — Schemas Zod en `RegisterPage.tsx` y `LoginPage.tsx`

Extender los schemas Zod de validación en los formularios de autenticación para **email y contraseña**:

**Campo `email`:**
- **Formato:** `z.string().email('Ingresa un correo electrónico válido.')` (mensaje en español).
- **Longitud mínima:** `.min(5, 'El correo es demasiado corto.')`.
- **Longitud máxima:** `.max(254, 'El correo no puede superar 254 caracteres.')`.
- **Sin espacios:** `.trim()` antes de la validación.

**Campo `password`:**
- **Longitud mínima consistente:** `.min(8, 'Mínimo 8 caracteres.')` en **todos** los formularios (registro y login).
- **Complejidad (solo registro):** regex que exija al menos 1 letra, 1 número y 1 carácter especial:
  ```typescript
  .regex(/^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?])/, 
    'La contraseña debe incluir al menos una letra, un número y un carácter especial.')
  ```
- La regla de complejidad aplica solo al registro (no al login, donde el usuario ya tiene su contraseña establecida).

### 4. Formularios afectados

| Formulario | Archivo | Campos afectados |
|---|---|---|
| Registro | `MVP_FrontEnd/src/features/auth/pages/RegisterPage.tsx` | `email` (paso 1), `password` (paso 1) |
| Login | `MVP_FrontEnd/src/features/auth/pages/LoginPage.tsx` | `email`, `password` |
| Serializer Registro | `MVP_PetTech/apps/usuarios/interfaces/serializers.py` | `email` y `password` en `RegistroSerializer` |
| Serializer Update | `MVP_PetTech/apps/usuarios/interfaces/serializers.py` | `email` en `UsuarioSerializer` |

## Contexto Técnico

- **Backend:** Django 5 + DRF. El modelo `Usuario` usa `email` como `USERNAME_FIELD` y tiene `unique=True`. El `UsuarioManager.create_user` ya llama `normalize_email()`.
- **Frontend:** React 18 + TypeScript + Zod + react-hook-form. La validación de email existe en `step1Schema` (registro) y `schema` (login) pero con mensajes en inglés o incompletos.
- **Auth:** JWT simplejwt. El email se incluye en el payload del token.

## Criterios de Aceptación (Alto Nivel)

1. El registro con un email inválido (sin `@`, sin dominio) retorna HTTP 400 con mensaje en español.
2. El registro con un email ya existente retorna HTTP 400 con el mensaje `'Este correo ya está registrado.'`.
3. El login con un email vacío retorna HTTP 400 con mensaje descriptivo antes de intentar autenticar.
4. En el frontend, el campo email muestra el error correspondiente al perder el foco (on-blur).
5. Los mensajes de error del campo email son consistentes en español entre todos los formularios.
6. El email se normaliza (trim + lowercase) antes de enviarse al backend.
7. El campo contraseña exige mínimo 8 caracteres en **todos** los formularios (registro y login).
8. En el registro, la contraseña debe incluir al menos una letra, un número y un carácter especial; si no cumple → mensaje de error claro.
9. En el login, la validación de contraseña solo verifica longitud mínima (sin regla de complejidad).

## Restricciones

- No modificar el modelo `Usuario` ni sus migraciones — las validaciones van en el serializer DRF y los schemas Zod.
- Usar terminología canónica: `correo` (no "mail", "e-mail"), `contraseña` (no "password").
- La regla de complejidad de contraseña aplica **solo al registro**, no al login.
- No romper el flujo de login ni registro existente.

## Prioridad

Media — es un requerimiento de calidad (UX + seguridad) que aplica al MVP.
