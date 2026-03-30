# TEST_CASES.md

---

## Información General

| Campo | Detalle |
|---|---|
| **Proyecto** | PetTech: Matcher de Adopción y Cuidados |
| **QA** | Elian Condor |
| **DEV** | Alejandra Marin |
| **Fecha** | 27/03/2026 |

---

# MICRO-SPRINT 1

**Período:** 24/03 – 25/03/2026
**HUs cubiertas:** HU-01 · HU-02 · HU-03 · HU-04 · HU-05 · HU-06

---

## HU-01 — Registrar información básica de la mascota

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-001 | HU-01 | **Dado** que el administrador está autenticado **Cuando** registra una mascota con datos válidos **Entonces** el sistema confirma el registro y la muestra en el listado | Positivo | Administrador autenticado. Formulario de registro disponible. | Nombre: "Luna", Especie: "Perro", Raza: "Labrador", Edad: 2, Sexo: "Hembra" | 1. Iniciar sesión como administrador. 2. Ir a "Registrar mascota". 3. Completar todos los campos obligatorios. 4. Guardar. | La mascota queda registrada y aparece en el listado con estado "disponible". | — | Crítico | Sin ejecutar |
| TC-002 | HU-01 | **Dado** que el administrador está autenticado **Cuando** intenta registrar una mascota con campos obligatorios vacíos **Entonces** el sistema muestra errores de validación y no guarda el registro | Negativo | Administrador autenticado. Formulario de registro disponible. | Nombre: "" (vacío), Especie: "" (vacío), Raza: "" (vacío) | 1. Iniciar sesión como administrador. 2. Ir a "Registrar mascota". 3. Dejar campos obligatorios vacíos. 4. Guardar. | El sistema muestra mensajes de error en los campos requeridos y no crea el registro. | — | Alto | Sin ejecutar |
| TC-003 | HU-01 | **Dado** que el administrador está autenticado **Cuando** intenta registrar una mascota con una edad inválida **Entonces** el sistema muestra un error de validación en el campo edad | Negativo | Administrador autenticado. Formulario de registro disponible. | Nombre: "Max", Especie: "Gato", Edad: -3 (valor negativo) | 1. Iniciar sesión como administrador. 2. Ir a "Registrar mascota". 3. Ingresar edad negativa. 4. Guardar. | El sistema muestra error: "La edad debe ser un valor positivo." y no guarda el registro. | — | Alto | Sin ejecutar |

---

## HU-02 — Registrar información de salud de la mascota

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-004 | HU-02 | **Dado** que el administrador tiene una mascota registrada **Cuando** registra su información de salud con datos válidos **Entonces** el sistema asocia los datos de salud al perfil de la mascota | Positivo | Mascota previamente registrada (TC-001 ejecutado). Administrador autenticado. | Vacunada: Sí, Esterilizada: No, Enfermedades: "Ninguna" | 1. Acceder al perfil de la mascota registrada. 2. Ir a "Información de salud". 3. Completar los campos. 4. Guardar. | Los datos de salud quedan vinculados a la mascota y visibles en su perfil. | — | Crítico | Sin ejecutar |
| TC-005 | HU-02 | **Dado** que el administrador registra salud de la mascota **Cuando** deja el historial de vacunas sin completar **Entonces** el sistema muestra error y no guarda el registro | Negativo | Administrador autenticado. Mascota previamente registrada (TC-001 ejecutado). | Historial vacunas: "" (vacío) | 1. Acceder al perfil de la mascota. 2. Ir a "Información de salud". 3. Dejar historial de vacunas vacío. 4. Guardar. | El sistema muestra: "El historial de vacunación es un dato requerido." y no guarda el registro. | — | Alto | Sin ejecutar |
| TC-006 | HU-02 | **Dado** que el administrador registra información de salud **Cuando** ingresa una fecha de vacunación futura **Entonces** el sistema rechaza la operación e informa que la fecha no puede ser futura | Negativo | Administrador autenticado. Mascota previamente registrada (TC-001 ejecutado). | Fecha vacunación: 01/12/2026 (fecha futura) | 1. Acceder al perfil de la mascota. 2. Ir a "Información de salud". 3. Ingresar fecha de vacunación futura. 4. Guardar. | El sistema muestra: "La fecha de vacunación no puede ser futura." y no guarda el registro. | — | Alto | Sin ejecutar |

---

## HU-03 — Subir fotos de la mascota

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-007 | HU-03 | **Dado** que el administrador accede al perfil de una mascota registrada **Cuando** sube una imagen en formato y tamaño válidos **Entonces** el sistema guarda la foto y la muestra en el perfil | Positivo | Mascota registrada. Administrador autenticado. | Archivo: "foto_luna.jpg", Tamaño: 2MB, Formato: JPG | 1. Acceder al perfil de la mascota. 2. Ir a "Subir foto". 3. Seleccionar archivo JPG de 2MB. 4. Confirmar subida. | La foto se muestra correctamente en el perfil de la mascota. | — | Alto | Sin ejecutar |
| TC-008 | HU-03 | **Dado** que el administrador accede al perfil de una mascota registrada **Cuando** intenta subir un archivo en formato no permitido **Entonces** el sistema rechaza el archivo y muestra los formatos válidos | Negativo | Mascota registrada. Administrador autenticado. | Archivo: "documento.pdf", Formato: PDF | 1. Acceder al perfil de la mascota. 2. Ir a "Subir foto". 3. Seleccionar archivo .pdf. 4. Confirmar subida. | El sistema muestra error: "Formato no permitido. Use JPG o PNG." y no guarda el archivo. | — | Medio | Sin ejecutar |
| TC-009 | HU-03 | **Dado** que el administrador accede al perfil de una mascota registrada **Cuando** intenta subir una imagen que supera el tamaño máximo permitido **Entonces** el sistema rechaza el archivo y notifica el límite de tamaño | Negativo | Mascota registrada. Administrador autenticado. | Archivo: "foto_grande.jpg", Tamaño: 8MB, Formato: JPG | 1. Acceder al perfil de la mascota. 2. Ir a "Subir foto". 3. Seleccionar archivo JPG de 8MB. 4. Confirmar subida. | El sistema muestra error: "El archivo supera el tamaño máximo de 5MB." y no guarda la imagen. | — | Medio | Sin ejecutar |

---

## HU-04 — Registrar información básica de familia adoptante

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-010 | HU-04 | **Dado** que una familia accede al formulario de registro **Cuando** completa todos los campos obligatorios con datos válidos **Entonces** el sistema crea el perfil familiar exitosamente | Positivo | Formulario de registro de familias disponible. | Nombre: "Familia García", Cédula: "1234567890", Teléfono: "0991234567", Dirección: "Quito, Pichincha" | 1. Acceder al formulario de registro de familia. 2. Completar todos los campos. 3. Hacer clic en "Registrarse". | El perfil de la familia queda registrado y se muestra mensaje de bienvenida. | — | Crítico | Sin ejecutar |
| TC-011 | HU-04 | **Dado** que una familia accede al formulario de registro **Cuando** ingresa una cédula con formato inválido **Entonces** el sistema muestra un error de validación y no crea el registro | Negativo | Formulario de registro de familias disponible. | Cédula: "123" (menos de 10 dígitos), Nombre: "Familia López" | 1. Acceder al formulario de registro. 2. Ingresar cédula con formato inválido. 3. Completar resto de campos. 4. Hacer clic en "Registrarse". | El sistema muestra error: "La cédula debe tener 10 dígitos." y no crea el registro. | — | Alto | Sin ejecutar |
| TC-012 | HU-04 | **Dado** que una familia accede al formulario de registro **Cuando** el solicitante es menor de edad **Entonces** el sistema rechaza el registro e indica el requisito de mayoría de edad | Negativo | Formulario de registro de familias disponible. | Nombre: "Carlos Pérez", Fecha de nacimiento: que resulte en edad menor a 18 años | 1. Acceder al formulario de registro. 2. Ingresar fecha de nacimiento de menor de edad. 3. Completar resto de campos. 4. Hacer clic en "Registrarse". | El sistema muestra error: "Debes ser mayor de edad para registrarte." y no crea el registro. | — | Alto | Sin ejecutar |
| TC-013 | HU-04 | **Dado** que ya existe una familia registrada con una cédula en el sistema **Cuando** otra familia intenta registrarse con la misma cédula **Entonces** el sistema rechaza el registro y notifica la duplicidad | Negativo | Familia con cédula "1234567890" previamente registrada (TC-010 ejecutado). | Cédula: "1234567890" (duplicada), Nombre: "Familia Rodríguez" | 1. Acceder al formulario de registro. 2. Ingresar cédula ya existente. 3. Completar resto de campos. 4. Hacer clic en "Registrarse". | El sistema muestra: "Esta cédula ya está registrada." y no crea duplicado. | — | Alto | Sin ejecutar |

---

## HU-05 — Registrar condiciones del hogar y experiencia

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-014 | HU-05 | **Dado** que la familia adoptante tiene un perfil registrado **Cuando** completa las condiciones del hogar con datos válidos **Entonces** el sistema almacena la información vinculada al perfil familiar | Positivo | Familia registrada (TC-010 ejecutado). | Tamaño hogar: "Grande", Niños: "Sí", Experiencia previa: "Sí", Tipo vivienda: "Casa" | 1. Acceder al perfil familiar. 2. Ir a "Condiciones del hogar". 3. Completar campos. 4. Guardar. | Las condiciones del hogar quedan guardadas y vinculadas al perfil familiar. | — | Crítico | Sin ejecutar |
| TC-015 | HU-05 | **Dado** que la familia completa condiciones del hogar **Cuando** omite el tipo de vivienda o el tamaño del hogar **Entonces** el sistema informa que los campos son obligatorios y no actualiza el perfil | Negativo | Familia registrada (TC-010 ejecutado). | Tipo vivienda: "" (vacío), Tamaño hogar: "" (vacío) | 1. Acceder al perfil familiar. 2. Ir a "Condiciones del hogar". 3. Omitir tipo de vivienda y tamaño. 4. Guardar. | El sistema informa que tipo de vivienda y tamaño del hogar son obligatorios. No actualiza el perfil. | — | Alto | Sin ejecutar |
| TC-016 | HU-05 | **Dado** que la familia adoptante ya tiene condiciones del hogar registradas **Cuando** intenta registrar la misma información como nuevo registro **Entonces** el sistema rechaza el registro por duplicidad | Negativo | Familia con condiciones del hogar ya registradas (TC-014 ejecutado). | Mismos datos de hogar ya existentes | 1. Acceder al perfil familiar. 2. Intentar crear nuevo registro de condiciones. 3. Guardar. | El sistema muestra: "El registro ya existe." y no crea duplicado. | — | Medio | Sin ejecutar |
| TC-017 | HU-05 | **Dado** que la familia adoptante está previamente registrada **Cuando** modifica la información de condiciones del hogar existente **Entonces** el sistema actualiza correctamente el perfil | Positivo | Familia con condiciones del hogar registradas (TC-014 ejecutado). | Tamaño hogar: "Mediano" (cambio desde "Grande") | 1. Acceder al perfil familiar. 2. Ir a "Condiciones del hogar". 3. Modificar el tamaño del hogar. 4. Guardar cambios. | El perfil se actualiza con la nueva información correctamente. | — | Alto | Sin ejecutar |

---

## HU-06 — Ver listado de mascotas disponibles

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-018 | HU-06 | **Dado** que existen mascotas con distintos estados en el sistema **Cuando** la familia adoptante accede al listado de mascotas **Entonces** el sistema muestra únicamente las mascotas con estado "disponible" | Positivo | Mascotas registradas con estados variados. Usuario autenticado. | N/A (consulta de listado) | 1. Iniciar sesión como familia adoptante. 2. Acceder a "Ver mascotas". 3. Revisar el listado. | Solo aparecen mascotas con estado "disponible". No se muestran las adoptadas o no disponibles. | — | Crítico | Sin ejecutar |
| TC-019 | HU-06 | **Dado** que no existen mascotas con estado "disponible" en el sistema **Cuando** la familia adoptante accede al listado de mascotas **Entonces** el sistema muestra un mensaje informando que no hay mascotas disponibles | Negativo | No existen mascotas con estado "disponible". Usuario autenticado. | N/A (listado vacío) | 1. Iniciar sesión como familia adoptante. 2. Acceder a "Ver mascotas". 3. Revisar el listado. | El sistema muestra mensaje: "No hay mascotas disponibles en este momento." sin errores. | — | Medio | Sin ejecutar |
| TC-020 | HU-06 | **Dado** que existen mascotas disponibles **Cuando** la familia adoptante consulta el listado **Entonces** cada mascota muestra la información relevante para su evaluación básica | Positivo | Mascotas disponibles registradas con datos completos. Usuario autenticado. | N/A (consulta de listado) | 1. Iniciar sesión como familia adoptante. 2. Acceder a "Ver mascotas". 3. Verificar los datos visibles por tarjeta. | Cada mascota muestra al menos: nombre, especie, edad, tamaño y foto. | — | Alto | Sin ejecutar |

---

## Resumen Micro-Sprint 1

| ID | HU | Escenario | Tipo | Prioridad | Estado |
|---|---|---|---|---|---|
| TC-001 | HU-01 | Registro exitoso de mascota | Positivo | Crítico | Sin ejecutar |
| TC-002 | HU-01 | Campos obligatorios vacíos | Negativo | Alto | Sin ejecutar |
| TC-003 | HU-01 | Edad con valor inválido | Negativo | Alto | Sin ejecutar |
| TC-004 | HU-02 | Registro de salud exitoso | Positivo | Crítico | Sin ejecutar |
| TC-005 | HU-02 | Historial de vacunas vacío | Negativo | Alto | Sin ejecutar |
| TC-006 | HU-02 | Fecha de vacunación futura | Negativo | Alto | Sin ejecutar |
| TC-007 | HU-03 | Subida de foto válida | Positivo | Alto | Sin ejecutar |
| TC-008 | HU-03 | Formato de archivo inválido | Negativo | Medio | Sin ejecutar |
| TC-009 | HU-03 | Imagen supera tamaño máximo | Negativo | Medio | Sin ejecutar |
| TC-010 | HU-04 | Registro de familia exitoso | Positivo | Crítico | Sin ejecutar |
| TC-011 | HU-04 | Cédula con formato inválido | Negativo | Alto | Sin ejecutar |
| TC-012 | HU-04 | Menor de edad rechazado | Negativo | Alto | Sin ejecutar |
| TC-013 | HU-04 | Registro duplicado rechazado | Negativo | Alto | Sin ejecutar |
| TC-014 | HU-05 | Condiciones del hogar guardadas | Positivo | Crítico | Sin ejecutar |
| TC-015 | HU-05 | Campos de hogar obligatorios faltantes | Negativo | Alto | Sin ejecutar |
| TC-016 | HU-05 | Registro duplicado de hogar rechazado | Negativo | Medio | Sin ejecutar |
| TC-017 | HU-05 | Actualización de condiciones del hogar | Positivo | Alto | Sin ejecutar |
| TC-018 | HU-06 | Listado solo muestra disponibles | Positivo | Crítico | Sin ejecutar |
| TC-019 | HU-06 | Listado vacío muestra mensaje | Negativo | Medio | Sin ejecutar |
| TC-020 | HU-06 | Información relevante visible en listado | Positivo | Alto | Sin ejecutar |

---

# MICRO-SPRINT 2

**Período:** 26/03 – 31/03/2026
**HUs cubiertas:** HU-07 · HU-08 · HU-09 · HU-10 · HU-11 · HU-12 · HU-13 · HU-14 · HU-15

---

## HU-07 — Ver detalle de mascota

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-021 | HU-07 | **Dado** que la familia adoptante está autenticada **Cuando** selecciona una mascota del listado **Entonces** el sistema muestra la información completa de la mascota | Positivo | Familia autenticada. Mascota con datos completos registrada. | ID mascota: 1, Nombre: "Luna" | 1. Iniciar sesión como familia adoptante. 2. Ir al listado de mascotas. 3. Seleccionar "Luna". 4. Verificar información mostrada. | Se muestran todos los datos: nombre, especie, raza, edad, sexo, nivel de energía, historia de la mascota. | — | Crítico | Sin ejecutar |
| TC-022 | HU-07 | **Dado** que la familia adoptante accede al detalle de una mascota **Cuando** la mascota tiene fotos asociadas **Entonces** el sistema muestra las fotografías en el perfil | Positivo | Mascota con al menos una foto cargada (TC-007 ejecutado). Familia autenticada. | ID mascota: 1 | 1. Iniciar sesión como familia adoptante. 2. Ir al detalle de la mascota. 3. Verificar sección de fotos. | Las fotos se cargan y muestran correctamente en el perfil. | — | Alto | Sin ejecutar |
| TC-023 | HU-07 | **Dado** que la familia adoptante accede al detalle de una mascota **Cuando** la mascota tiene información de salud registrada **Entonces** el sistema muestra su historial básico de salud | Positivo | Mascota con información de salud registrada (TC-004 ejecutado). Familia autenticada. | ID mascota: 1 | 1. Iniciar sesión como familia adoptante. 2. Ir al detalle de la mascota. 3. Verificar sección de salud. | Se muestran los datos de salud: estado de vacunación, esterilización, enfermedades conocidas. | — | Alto | Sin ejecutar |
| TC-024 | HU-07 | **Dado** que la familia adoptante intenta acceder al detalle de una mascota **Cuando** el ID de la mascota no existe en el sistema **Entonces** el sistema muestra un mensaje de error informativo | Negativo | Familia autenticada. | ID mascota: 9999 (no existente) | 1. Iniciar sesión como familia adoptante. 2. Acceder manualmente a la URL del detalle con ID inexistente. | El sistema retorna mensaje: "La mascota solicitada no existe." sin romper la aplicación. | — | Alto | Sin ejecutar |

---

## HU-08 — Solicitar adopción

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-025 | HU-08 | **Dado** que la familia adoptante está autenticada y tiene perfil completo **Cuando** selecciona una mascota disponible y confirma la solicitud **Entonces** el sistema registra la solicitud con estado "pendiente" | Positivo | Familia autenticada con perfil completo (TC-010 y TC-014 ejecutados). Mascota con estado "disponible". | ID mascota: 1, ID familia: 1 | 1. Iniciar sesión como familia adoptante. 2. Ir al detalle de la mascota. 3. Hacer clic en "Solicitar adopción". 4. Confirmar la solicitud. | La solicitud queda registrada con estado "pendiente". El sistema muestra confirmación. | — | Crítico | Sin ejecutar |
| TC-026 | HU-08 | **Dado** que la familia adoptante envió una solicitud **Cuando** la solicitud es registrada en el sistema **Entonces** el estado inicial debe ser "pendiente" y no "aprobada" ni "rechazada" | Positivo | Solicitud recién creada (TC-025 ejecutado). | ID solicitud: 1 | 1. Verificar en el sistema el estado de la solicitud recién creada. | El estado es exactamente "pendiente", no "aprobada" ni "rechazada". | — | Crítico | Sin ejecutar |
| TC-027 | HU-08 | **Dado** que una mascota tiene estado distinto a "disponible" **Cuando** la familia adoptante intenta enviar una solicitud de adopción **Entonces** el sistema rechaza la solicitud y notifica la no disponibilidad | Negativo | Mascota con estado "adoptada". Familia autenticada. | ID mascota: 2 (estado: "adoptada") | 1. Iniciar sesión como familia adoptante. 2. Intentar solicitar la mascota no disponible. | El sistema muestra: "Esta mascota no está disponible para adopción." y no registra la solicitud. | — | Crítico | Sin ejecutar |
| TC-028 | HU-08 | **Dado** que una familia ya tiene una solicitud activa sobre una mascota **Cuando** intenta enviar una segunda solicitud para la misma mascota **Entonces** el sistema rechaza el duplicado | Negativo | Solicitud previa existente (TC-025 ejecutado). Mascota aún disponible. | ID mascota: 1, ID familia: 1 (ya con solicitud activa) | 1. Iniciar sesión como la misma familia. 2. Intentar solicitar la misma mascota nuevamente. | El sistema muestra: "Ya tienes una solicitud activa para esta mascota." y no crea duplicado. | — | Alto | Sin ejecutar |

---

## HU-09 — Consultar detalle de solicitud de adopción

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-029 | HU-09 | **Dado** que existe una solicitud de adopción registrada **Cuando** el administrador accede a su detalle **Entonces** el sistema muestra los datos de la familia y de la mascota asociada | Positivo | Administrador autenticado. Solicitud existente (TC-025 ejecutado). | ID solicitud: 1 | 1. Iniciar sesión como administrador. 2. Ir a "Solicitudes de adopción". 3. Seleccionar la solicitud con ID 1. | Se muestra: nombre familia, cédula, condiciones del hogar, nombre mascota, especie, características. | — | Crítico | Sin ejecutar |
| TC-030 | HU-09 | **Dado** que el administrador intenta acceder al detalle de una solicitud **Cuando** el ID de la solicitud no existe en el sistema **Entonces** el sistema informa que la solicitud no fue encontrada | Negativo | Administrador autenticado. | ID solicitud: 9999 (no existente) | 1. Iniciar sesión como administrador. 2. Intentar acceder al detalle con ID inexistente. | El sistema muestra: "La solicitud consultada no existe en el sistema." sin error 500. | — | Alto | Sin ejecutar |

---

## HU-10 — Registrar decisión sobre solicitud

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-031 | HU-10 | **Dado** que existe una solicitud con estado "pendiente" **Cuando** el administrador decide aprobarla **Entonces** el sistema actualiza el estado a "aprobada" | Positivo | Administrador autenticado. Solicitud con estado "pendiente" (TC-025 ejecutado). | ID solicitud: 1, Acción: "Aprobar" | 1. Iniciar sesión como administrador. 2. Acceder al detalle de la solicitud. 3. Hacer clic en "Aprobar". 4. Confirmar acción. | El estado de la solicitud cambia a "aprobada". | — | Crítico | Sin ejecutar |
| TC-032 | HU-10 | **Dado** que existe una solicitud con estado "pendiente" **Cuando** el administrador decide rechazarla **Entonces** el sistema actualiza el estado a "rechazada" | Positivo | Administrador autenticado. Solicitud con estado "pendiente". | ID solicitud: 2, Acción: "Rechazar" | 1. Iniciar sesión como administrador. 2. Acceder al detalle de la solicitud. 3. Hacer clic en "Rechazar". 4. Confirmar acción. | El estado de la solicitud cambia a "rechazada". | — | Crítico | Sin ejecutar |
| TC-033 | HU-10 | **Dado** que existe una solicitud con estado "aprobada" **Cuando** el administrador intenta cambiar su estado nuevamente **Entonces** el sistema bloquea la operación e informa que ya tiene decisión final | Negativo | Administrador autenticado. Solicitud con estado "aprobada" (TC-031 ejecutado). | ID solicitud: 1, Acción: intentar "Rechazar" | 1. Iniciar sesión como administrador. 2. Acceder al detalle de la solicitud aprobada. 3. Intentar cambiar el estado. | El sistema muestra: "Esta solicitud ya tiene una decisión final y no puede modificarse." | — | Crítico | Sin ejecutar |
| TC-034 | HU-10 | **Dado** que existe una solicitud con estado "rechazada" **Cuando** el administrador intenta aprobarla **Entonces** el sistema bloquea la operación e informa que ya tiene decisión final | Negativo | Administrador autenticado. Solicitud con estado "rechazada" (TC-032 ejecutado). | ID solicitud: 2, Acción: intentar "Aprobar" | 1. Iniciar sesión como administrador. 2. Acceder al detalle de la solicitud rechazada. 3. Intentar cambiar el estado. | El sistema muestra: "Esta solicitud ya tiene una decisión final y no puede modificarse." | — | Alto | Sin ejecutar |

---

## HU-11 — Sugerir alternativa de adopción

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-035 | HU-11 | **Dado** que el administrador revisa el perfil de una familia **Cuando** el sistema analiza los datos del hogar contra las mascotas disponibles **Entonces** muestra indicadores de compatibilidad basados en las reglas de negocio | Positivo | Administrador autenticado. Familia con perfil completo. Mascotas disponibles registradas. | ID familia: 1 (hogar grande, sin niños, con experiencia) | 1. Iniciar sesión como administrador. 2. Acceder al perfil de la familia. 3. Revisar indicadores de compatibilidad. | El sistema muestra porcentaje o nivel de compatibilidad por cada mascota disponible. | — | Crítico | Sin ejecutar |
| TC-036 | HU-11 | **Dado** que el administrador identifica una mascota compatible **Cuando** registra la sugerencia de adopción para esa familia **Entonces** el sistema guarda la sugerencia correctamente | Positivo | Administrador autenticado. Familia registrada. Mascota disponible con compatibilidad alta. | ID familia: 1, ID mascota sugerida: 3 | 1. Iniciar sesión como administrador. 2. Ir al perfil de la familia. 3. Seleccionar mascota sugerida. 4. Confirmar sugerencia. | La sugerencia queda registrada y visible en el perfil de la familia. | — | Crítico | Sin ejecutar |
| TC-037 | HU-11 | **Dado** que el administrador intenta sugerir una mascota **Cuando** la mascota seleccionada ya está en proceso de adopción **Entonces** el sistema invalida la operación e informa que no está disponible | Negativo | Administrador autenticado. Mascota con estado "en proceso". | ID mascota: 1 (estado: en proceso), ID familia: 2 | 1. Iniciar sesión como administrador. 2. Intentar sugerir mascota no disponible a la familia. | El sistema muestra: "La mascota no se encuentra disponible para adopción." y no registra la sugerencia. | — | Alto | Sin ejecutar |
| TC-038 | HU-11 | **Dado** que el sistema evalúa la compatibilidad entre familia y mascota **Cuando** el tamaño de la mascota supera la capacidad del hogar **Entonces** el sistema indica incompatibilidad alta para esa combinación | Negativo | Familia con hogar pequeño registrada. Mascota de tamaño grande disponible. | ID familia: 3 (hogar: pequeño), ID mascota: 4 (tamaño: grande) | 1. Iniciar sesión como administrador. 2. Revisar compatibilidad de familia 3 con mascota 4. | El sistema muestra indicador de incompatibilidad alta por tamaño de hogar. | — | Alto | Sin ejecutar |

---

## HU-12 — Confirmar adopción

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-039 | HU-12 | **Dado** que existe una solicitud con estado "aprobada" **Cuando** el administrador confirma la adopción **Entonces** el sistema registra la adopción como exitosa, vincula mascota y familia, y actualiza el estado de la mascota a "adoptada" | Positivo | Administrador autenticado. Solicitud con estado "aprobada" (TC-031 ejecutado). | ID solicitud: 1 | 1. Iniciar sesión como administrador. 2. Acceder a la solicitud aprobada. 3. Hacer clic en "Confirmar adopción". 4. Verificar resultados. | Estado solicitud: "adopción exitosa". Estado mascota: "adoptada". Fecha de adopción registrada automáticamente. Mascota vinculada a la familia. | — | Crítico | Sin ejecutar |
| TC-040 | HU-12 | **Dado** que existe una solicitud con estado "pendiente" **Cuando** el administrador intenta confirmar la adopción directamente **Entonces** el sistema rechaza la operación indicando que solo se confirman solicitudes aprobadas | Negativo | Administrador autenticado. Solicitud con estado "pendiente". | ID solicitud: 3 (estado: pendiente) | 1. Iniciar sesión como administrador. 2. Acceder a la solicitud pendiente. 3. Intentar confirmar la adopción. | El sistema muestra: "Solo se pueden confirmar solicitudes con estado aprobada." | — | Crítico | Sin ejecutar |
| TC-041 | HU-12 | **Dado** que existe una solicitud ya confirmada con estado "adopción exitosa" **Cuando** el administrador intenta confirmarla nuevamente **Entonces** el sistema bloquea la operación e informa que ya fue confirmada | Negativo | Administrador autenticado. Solicitud con estado "adopción exitosa" (TC-039 ejecutado). | ID solicitud: 1 (estado: adopción exitosa) | 1. Iniciar sesión como administrador. 2. Acceder a la solicitud ya confirmada. 3. Intentar confirmar nuevamente. | El sistema muestra: "Esta adopción ya fue confirmada previamente." | — | Alto | Sin ejecutar |

---

## HU-13 — Visualizar adopciones realizadas

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-042 | HU-13 | **Dado** que el administrador accede al sistema **Cuando** navega a la sección "Adopciones realizadas" **Entonces** el sistema muestra el historial de adopciones exitosas | Positivo | Administrador autenticado. Al menos una adopción confirmada (TC-039 ejecutado). | N/A (consulta de historial) | 1. Iniciar sesión como administrador. 2. Ir a "Adopciones realizadas". 3. Verificar listado. | Se muestran las adopciones con estado "adopción exitosa" con fecha y datos de familia y mascota. | — | Crítico | Sin ejecutar |
| TC-043 | HU-13 | **Dado** que el administrador visualiza el historial de adopciones **Cuando** aplica un filtro por usuario específico **Entonces** el sistema muestra únicamente las adopciones asociadas a ese usuario | Positivo | Administrador autenticado. Múltiples adopciones de distintos usuarios registradas. | Filtro: nombre familia "Familia García" | 1. Iniciar sesión como administrador. 2. Ir a "Adopciones realizadas". 3. Aplicar filtro por usuario "Familia García". | Solo aparecen las adopciones de "Familia García". | — | Alto | Sin ejecutar |
| TC-044 | HU-13 | **Dado** que no existen adopciones registradas en el sistema **Cuando** el administrador accede al historial **Entonces** el sistema muestra un mensaje informativo de lista vacía | Negativo | Administrador autenticado. Sin adopciones confirmadas en el sistema. | N/A (historial vacío) | 1. Iniciar sesión como administrador en entorno limpio. 2. Ir a "Adopciones realizadas". | El sistema muestra: "No hay adopciones registradas aún." sin errores ni tabla vacía sin mensaje. | — | Medio | Sin ejecutar |

---

## HU-14 — Generar calendario de vacunas

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-045 | HU-14 | **Dado** que existe una adopción confirmada **Cuando** la adopción es registrada como exitosa **Entonces** el sistema genera automáticamente un calendario de vacunación y lo asocia a la adopción | Positivo | Adopción confirmada (TC-039 ejecutado). Mascota con especie, edad e historial de vacunación registrados. | ID adopción: 1 | 1. Confirmar adopción (TC-039). 2. Verificar en la adopción que el calendario fue generado. | El calendario de vacunación queda creado y vinculado a la adopción. | — | Crítico | Sin ejecutar |
| TC-046 | HU-14 | **Dado** que una mascota adoptada es un cachorro de perro sin vacunas previas **Cuando** se genera el calendario de vacunación **Entonces** el sistema asigna el esquema de cachorros con refuerzos frecuentes (Parvovirus, Moquillo) | Positivo | Adopción confirmada. Mascota: especie "Perro", edad < 1 año, historial de vacunas: ninguna. | Especie: "Perro", Edad: 3 meses, Vacunas previas: ninguna | 1. Confirmar adopción con mascota cachorro sin vacunas. 2. Consultar calendario generado. | El calendario incluye: Parvovirus, Moquillo, con frecuencia de refuerzos cada 3-4 semanas según protocolo de cachorros. | — | Crítico | Sin ejecutar |
| TC-047 | HU-14 | **Dado** que una mascota adoptada es un gato adulto con vacunas parciales **Cuando** se genera el calendario de vacunación **Entonces** el sistema asigna solo las vacunas faltantes con frecuencia anual o trianual | Positivo | Adopción confirmada. Mascota: especie "Gato", edad > 1 año, historial: Panleucopenia aplicada. | Especie: "Gato", Edad: 3 años, Vacunas previas: "Panleucopenia" | 1. Confirmar adopción con mascota gato adulto con vacuna parcial. 2. Consultar calendario generado. | El calendario incluye: Calicivirus (pendiente) con frecuencia anual. No repite Panleucopenia ya aplicada. | — | Crítico | Sin ejecutar |
| TC-048 | HU-14 | **Dado** que una mascota adoptada es un perro adulto con esquema de vacunación completo **Cuando** se genera el calendario **Entonces** el sistema asigna únicamente los refuerzos anuales o trianuales correspondientes | Positivo | Adopción confirmada. Mascota: especie "Perro", edad > 1 año, historial: todas las vacunas aplicadas. | Especie: "Perro", Edad: 4 años, Vacunas: esquema completo | 1. Confirmar adopción con perro adulto con esquema completo. 2. Consultar calendario generado. | El calendario muestra únicamente refuerzos con fechas sugeridas anuales/trianuales. No incluye vacunas de cachorro. | — | Alto | Sin ejecutar |
| TC-049 | HU-14 | **Dado** que el calendario fue generado **Cuando** se revisan las vacunas incluidas **Entonces** cada vacuna tiene una fecha sugerida asignada a partir de la fecha de adopción | Positivo | Calendario generado (TC-045 ejecutado). Fecha de adopción: 27/03/2026. | ID adopción: 1 | 1. Acceder al calendario de la adopción. 2. Verificar que cada vacuna tiene fecha sugerida. | Cada vacuna del calendario tiene una fecha futura sugerida calculada desde la fecha de adopción. | — | Alto | Sin ejecutar |

---

## HU-15 — Consultar calendario de vacunación

| ID | HU | Escenario Gherkin | Tipo | Precondiciones | Datos de entrada | Pasos de ejecución | Resultado esperado | Resultado obtenido | Prioridad | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-050 | HU-15 | **Dado** que la familia adoptante completó una adopción exitosa **Cuando** accede a la información de su mascota **Entonces** el sistema muestra el calendario de vacunación con las fechas correspondientes | Positivo | Familia autenticada. Adopción confirmada y calendario generado (TC-045 ejecutado). | ID familia: 1, ID mascota: 1 | 1. Iniciar sesión como familia adoptante. 2. Ir a "Mi mascota". 3. Verificar sección de calendario. | Se muestra el calendario con vacunas y fechas sugeridas claramente. | — | Crítico | Sin ejecutar |
| TC-051 | HU-15 | **Dado** que la familia adoptante tiene una solicitud en estado "pendiente" **Cuando** intenta acceder al calendario de vacunación de esa mascota **Entonces** el sistema no muestra el calendario ya que la adopción no está confirmada | Negativo | Familia autenticada. Solicitud con estado "pendiente" (TC-025 ejecutado). Mascota aún no entregada. | ID familia: 1, ID solicitud: 1 (pendiente) | 1. Iniciar sesión como familia adoptante. 2. Intentar acceder al calendario de la mascota solicitada. | El sistema no muestra el calendario. Indica: "El calendario estará disponible una vez confirmada la adopción." | — | Crítico | Sin ejecutar |
| TC-052 | HU-15 | **Dado** que un usuario no tiene ninguna adopción registrada **Cuando** intenta acceder al calendario de vacunación de una mascota **Entonces** el sistema deniega el acceso | Negativo | Familia autenticada sin adopciones registradas. | ID mascota: 1 (pertenece a otra familia) | 1. Iniciar sesión como familia sin adopciones. 2. Intentar acceder al calendario de una mascota que no le corresponde. | El sistema muestra: "No tienes acceso al calendario de esta mascota." y deniega la visualización. | — | Alto | Sin ejecutar |

---

## Resumen Micro-Sprint 2

| ID | HU | Escenario | Tipo | Prioridad | Estado |
|---|---|---|---|---|---|
| TC-021 | HU-07 | Visualización completa del detalle de mascota | Positivo | Crítico | Sin ejecutar |
| TC-022 | HU-07 | Visualización de fotos en el detalle | Positivo | Alto | Sin ejecutar |
| TC-023 | HU-07 | Visualización de historial de salud en el detalle | Positivo | Alto | Sin ejecutar |
| TC-024 | HU-07 | Detalle de mascota con ID inexistente | Negativo | Alto | Sin ejecutar |
| TC-025 | HU-08 | Solicitud exitosa con estado pendiente | Positivo | Crítico | Sin ejecutar |
| TC-026 | HU-08 | Estado inicial de solicitud es pendiente | Positivo | Crítico | Sin ejecutar |
| TC-027 | HU-08 | Solicitud rechazada por mascota no disponible | Negativo | Crítico | Sin ejecutar |
| TC-028 | HU-08 | Solicitud duplicada rechazada | Negativo | Alto | Sin ejecutar |
| TC-029 | HU-09 | Consulta de detalle de solicitud por administrador | Positivo | Crítico | Sin ejecutar |
| TC-030 | HU-09 | Consulta de solicitud con ID inexistente | Negativo | Alto | Sin ejecutar |
| TC-031 | HU-10 | Aprobación de solicitud pendiente | Positivo | Crítico | Sin ejecutar |
| TC-032 | HU-10 | Rechazo de solicitud pendiente | Positivo | Crítico | Sin ejecutar |
| TC-033 | HU-10 | Cambio en solicitud aprobada bloqueado | Negativo | Crítico | Sin ejecutar |
| TC-034 | HU-10 | Cambio en solicitud rechazada bloqueado | Negativo | Alto | Sin ejecutar |
| TC-035 | HU-11 | Visualización de indicadores de compatibilidad | Positivo | Crítico | Sin ejecutar |
| TC-036 | HU-11 | Registro de sugerencia de adopción exitosa | Positivo | Crítico | Sin ejecutar |
| TC-037 | HU-11 | Sugerencia de mascota no disponible bloqueada | Negativo | Alto | Sin ejecutar |
| TC-038 | HU-11 | Incompatibilidad alta por tamaño de hogar | Negativo | Alto | Sin ejecutar |
| TC-039 | HU-12 | Confirmación de adopción exitosa | Positivo | Crítico | Sin ejecutar |
| TC-040 | HU-12 | Confirmar solicitud pendiente bloqueado | Negativo | Crítico | Sin ejecutar |
| TC-041 | HU-12 | Re-confirmación de adopción bloqueada | Negativo | Alto | Sin ejecutar |
| TC-042 | HU-13 | Visualización del historial de adopciones | Positivo | Crítico | Sin ejecutar |
| TC-043 | HU-13 | Filtrado de adopciones por usuario | Positivo | Alto | Sin ejecutar |
| TC-044 | HU-13 | Historial vacío muestra mensaje informativo | Negativo | Medio | Sin ejecutar |
| TC-045 | HU-14 | Generación automática del calendario al confirmar adopción | Positivo | Crítico | Sin ejecutar |
| TC-046 | HU-14 | Calendario para cachorro de perro sin vacunas | Positivo | Crítico | Sin ejecutar |
| TC-047 | HU-14 | Calendario para gato adulto con vacunas parciales | Positivo | Crítico | Sin ejecutar |
| TC-048 | HU-14 | Calendario para perro adulto con esquema completo | Positivo | Alto | Sin ejecutar |
| TC-049 | HU-14 | Fechas sugeridas asignadas a cada vacuna | Positivo | Alto | Sin ejecutar |
| TC-050 | HU-15 | Familia consulta calendario tras adopción exitosa | Positivo | Crítico | Sin ejecutar |
| TC-051 | HU-15 | Calendario no visible con solicitud pendiente | Negativo | Crítico | Sin ejecutar |
| TC-052 | HU-15 | Acceso denegado a calendario de mascota ajena | Negativo | Alto | Sin ejecutar |

---

# Resumen General — Ambos Sprints

| Sprint | Total Casos | Críticos | Altos | Medios | Bajos | Sin ejecutar |
|---|---|---|---|---|---|---|
| Micro-Sprint 1 | 20 | 6 | 9 | 3 | 0 | 20 |
| Micro-Sprint 2 | 32 | 18 | 12 | 2 | 0 | 32 |
| **Total** | **52** | **24** | **21** | **5** | **0** | **52** |

---

*Documento elaborado por: Elian Condor (QA) — Revisado por: Alejandra Marin (DEV) — Fecha: 27/03/2026*
