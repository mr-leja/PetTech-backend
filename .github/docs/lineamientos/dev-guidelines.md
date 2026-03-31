
# Resumen de Lineamientos de Desarrollo (CoE DevArq)

Este documento centraliza los principios y reglas **obligatorias** para garantizar que el software diseñado, construido y desplegado sea seguro, limpio, mantenible y resiliente. 

---

### 1. Codificación Segura por Defecto (LIN-DEV-003)
**Objetivo:** Integrar la seguridad desde el diseño para proteger datos y eliminar vulnerabilidades conocidas antes del despliegue.
*   **Validación Estricta:** Toda entrada de datos externos debe ser validada (mediante schemas declarativos) y sanitizada en el punto de entrada.
*   **Prevención de Inyecciones:** Es obligatorio usar consultas 100% parametrizadas (SQL, NoSQL, OS, etc.). Se prohíbe la concatenación de strings.
*   **Control de Acceso:** Todo endpoint debe requerir autenticación y autorización robusta. Cero credenciales hardcodeadas.
*   **Protección de Datos:** Cifrado obligatorio de datos sensibles tanto en tránsito (TLS) como en reposo.
*   **Protección en Logs y Errores:** Prohibido registrar PII o datos sensibles en logs. Los mensajes de error no deben revelar detalles internos como *stack traces* o rutas al cliente.
*   **Pipelines y Secretos:** Uso bloqueante de SAST y análisis de dependencias (SCA) en el pipeline de CI. Cero secretos (API keys, tokens) en código fuente, configuraciones o historial de Git.

### 2. Código Limpio / Clean Code (LIN-DEV-001)
**Objetivo:** Producir código legible, mantenible y autoexplicativo.
*   **Claridad:** El código debe transmitir su intención con nombres descriptivos (alineados al dominio de negocio). Se prohíben comentarios que traduzcan lo obvio o etiquetas "TODO" en ramas protegidas.
*   **Responsabilidad Única (SRP):** Las funciones deben hacer una sola cosa. Límites: ≤ 50 líneas (LOC), complejidad ciclomática ≤ 10, y máximo 5 parámetros.
*   **Eliminación de Deuda:** No debe existir código duplicado, código muerto ni "valores mágicos" no declarados como constantes.
*   **Tipado y Estructura:** Tipos explícitos obligatorios en APIs públicas (se prohíbe el uso de `any` o `dynamic`). Los archivos no deben exceder las 400 líneas y se prohíben las dependencias circulares.

### 3. Principios de Diseño — Clean Architecture (LIN-DEV-002)
**Objetivo:** Asegurar bajo acoplamiento, alta cohesión y testabilidad mediante Clean Architecture.
*   **Cumplimiento SOLID:** Respetar estrictamente los 5 principios. Las clases deben tener una sola responsabilidad, el código debe estar cerrado a modificaciones, y las dependencias deben estar invertidas mediante abstracciones.
*   **Capas Definidas (Clean Architecture):** El proyecto sigue la separación `domain/ → infrastructure/ → interfaces/`. La capa `domain/` no debe importar librerías de infraestructura (Django ORM, DRF). La capa `infrastructure/` (repositories) es el único lugar con acceso a la base de datos PostgreSQL.
*   **Testabilidad:** Las entidades de dominio deben instanciarse sin infraestructura real. Los repositories se inyectan en las vistas (interfaces) — nunca al revés.
*   **Resiliencia y Excepciones:** Las llamadas a servicios externos (ej. Cloudinary) requieren manejo explícito de errores con *timeouts*. Se prohíben los bloques `except` vacíos o silenciados. No usar patrones de microservicios como *circuit breakers* o *DLQ* — no aplican al monolito Django.

### 4. Diseño de APIs REST (LIN-DEV-010)
**Objetivo:** Crear APIs interoperables, seguras y evolucionables con Django REST Framework.
*   **URIs Semánticas:** Usar siempre sustantivos en plural para los recursos y los métodos HTTP correctos (POST = crear, PUT/PATCH = modificar, GET = leer, DELETE = eliminar).
*   **Respuestas Estándar DRF:** Usar los serializers DRF para la respuesta. Los errores de validación retornan HTTP 400 con detalle de campos. Los errores de negocio usan excepciones de dominio capturadas en `core/exception_handler.py`.
*   **Idempotencia:** Las operaciones de escritura (POST/PUT/PATCH) deben ser idempotentes donde sea posible — usar validaciones en el serializer para evitar duplicados.
*   **Evolución:** Prefijo `/api/v1/` obligatorio en todas las rutas. Los *breaking changes* solo se permiten con una nueva versión de URL.
*   **Controles de Datos:** Colecciones requieren paginación obligatoria (usar `core/pagination.py`). Filtrado y búsquedas por *query parameters*.
*   **Permisos:** Toda vista debe declarar `permission_classes` explícitamente. Usar `core/permissions.py` para los permisos personalizados (`ADMIN`, `FAMILIA`).

### 5. Datos y Persistencia (LIN-DEV-012)
**Objetivo:** Hacer el acceso a datos consistente, auditable y resistente a errores de rendimiento.
*   **Esquema como Código:** Toda alteración a la Base de Datos se hace mediante *migraciones versionadas* en el repositorio. Éstas siempre deben ser compatibles hacia atrás (backward-compatible).
*   **Convenciones Universales:** Nombrado de objetos en `snake_case` y plural. Toda tabla de negocio debe tener campos de auditoría (`created_at`, `updated_at`) y estrategia de *soft delete* unificada (`deleted_at`).
*   **Rendimiento:** Las columnas usadas en filtros o cruces (`WHERE`, `JOIN`) requieren índices. Se prohíbe el antipatrón N+1 queries (no iterar llamadas en bucles).
*   **Transacciones y Pooling:** *Connection pooling* obligatorio. Las transacciones de base de datos no deben englobar llamadas de red externas a otros servicios.

### 6. Separación de Capas — Clean Architecture (LIN-DEV-013)
**Objetivo:** Preservar la separación de responsabilidades entre las capas del monolito Django de PetTech.
*   **Regla de dependencia:** Las importaciones solo pueden fluir hacia adentro: `interfaces/ → infrastructure/ → domain/`. Prohibido que `domain/` importe de `infrastructure/` o `interfaces/`.
*   **`domain/`:** Solo entidades Python puras (`dataclasses` o clases simples) y excepciones de negocio. Sin imports de Django, DRF ni librerías externas.
*   **`infrastructure/`:** Modelos Django ORM (`models.py`) y repositorios (`repositories.py`). Es el único lugar donde se hacen queries a PostgreSQL. Los repositories exponen métodos de negocio (no queries SQL crudas).
*   **`interfaces/`:** ViewSets y APIViews DRF (`views.py`), serializers (`serializers.py`) y rutas (`urls.py`). Delegan toda lógica de acceso a datos a los repositories — nunca hacen queries ORM directamente.
*   **`config/`:** Configuración de Django (`settings/`), URL raíz (`urls.py`). Registra los routers de cada módulo. Sin lógica de negocio.
*   **`core/`:** Utilidades transversales (`permissions.py`, `pagination.py`, `exception_handler.py`). Pueden ser importadas por cualquier capa.

### 7. Estrategia de Testing (LIN-DEV-005)
**Objetivo:** Automatización de pruebas bajo la "pirámide de testing" y prevención de regresiones.
*   **Cobertura:** La cobertura de código en lógica de negocio debe ser de **≥ 80%**, y este umbral funciona como un *quality gate* bloqueante en CI.
*   **Distribución:** Debe priorizarse pruebas unitarias (~70%), integraciones (~20%) y E2E (~10%).
*   **Determinismo:** Los tests no deben depender del orden de ejecución, base de datos de producción, fechas, o usar `sleep` para sincronización temporal (cero tests intermitentes o "flaky").
*   **Metodología:** Desarrollo dirigido por pruebas (TDD) es requerido para lógica crítica, y se exige pruebas de contrato (CDC) para APIs expuestas.

### 8. Observabilidad (LIN-DEV-007)
**Objetivo:** La aplicación Django debe generar logs estructurados y exponer estado de salud por defecto.
*   **Logging:** Usar el sistema de logging de Django (`LOGGING` en `settings/`). Los logs deben incluir nivel, módulo y mensaje descriptivo. Se prohíbe registrar PII (emails, contraseñas, tokens JWT) en logs.
*   **Errores no controlados:** Todo error 500 debe quedar registrado en los logs del servidor con suficiente contexto para diagnosticar — sin exponer stack traces al cliente en respuestas HTTP.
*   **Estado (Health):** Exponer un endpoint `/api/health/` que retorne HTTP 200 cuando la app y la conexión a PostgreSQL están operativas. Se usa para el healthcheck de Docker Compose.
*   **No aplicable a este proyecto:** Trazabilidad distribuida con OpenTelemetry, Dead Letter Queues, Circuit Breakers — son patrones de microservicios que no aplican al monolito Django de PetTech.

### 9. Revisión de Pares / Code Review (LIN-DEV-004)
**Objetivo:** Asegurar calidad colaborativa y que ningún código entre a producción sin una validación explícita.
*   **Proceso Bloqueante:** TODO cambio requiere pasar por un Pull Request y tener al menos **1 aprobación** de un revisor (≥ 2 para módulos *core*) antes de ingresar a ramas principales.
*   **Calidad de la Revisión:** El PR debe poseer una buena descripción y estar avalado contra todo el checklist de normas CoE (diseño, seguridad, pruebas). Las correcciones requeridas (`blocking:`) evitan la aprobación hasta ser solucionadas.
*   **Eficiencia:** Los PRs no deben sobrepasar las 400 líneas modificadas, y los tiempos de primera respuesta por revisores deben ser ≤ 4 horas.

### 10. Documentación Técnica (LIN-DEV-009)
**Objetivo:** Evitar silos de conocimiento atando la documentación directamente al código.
*   **README y Onboarding:** Todo proyecto debe contar con un `README.md` exhaustivo y un proceso que permita a un desarrollador nuevo ejecutar el sistema en ≤ 1 día.
*   **Mantenimiento "In-Pull":** Toda documentación afectada por un código debe modificarse **en el mismo PR** (API, Diagramas, Runbooks).
*   **Formatos Claros:** Decisiones de diseño en registros de arquitectura (ADRs); diagramas con el *C4 Model*; manuales y *Runbooks* en repositorios productivos para respuesta a incidentes.
*   **Validación:** Documentación estructurada (ej. OpenAPI/AsyncAPI) debe ser comprobada automáticamente en el Pipeline de CI (linter de contratos).

### 11. Versionamiento y Entrega Continua (LIN-DEV-008)
**Objetivo:** Mantener un historial de Git predecible como fuente de la verdad para empaquetamiento y despliegue.
*   **Convenciones Rigurosas:** Uso imperativo de *Conventional Commits* (`feat:`, `fix:`, `chore:`, etc.) que en conjunto alimentan de forma automática la regla de Versionamiento Semántico (*SemVer*) y la creación de notas (*Changelogs*).
*   **CI como Guardián:** Implementación de *Quality Gates* bloqueantes. Falla el merge si la cobertura no alcanza o si las herramientas de escaneo (SAST/SCA) arrojan vulnerabilidades altas/críticas.
*   **Seguridad de Operaciones:** Absolutamente cero secretos en pipelines (usar Vaults o mecanismos nativos). Ramas protegidas; prohibido empujar directamente al `main` o borrar el historial.
*   **Reproducibilidad:** Fijar dependencias explícitas (*lock files*) y etiquetas de imágenes en Docker.

---
*Este documento resume los pilares técnicos del CoE DevArq. Toda desviación a reglas marcadas como `Critical` amerita resolución inmediata o excepciones justificadas formalmente con mitigación de riesgos y fecha de caducidad aprobada.*