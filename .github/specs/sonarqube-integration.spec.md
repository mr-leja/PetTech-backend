---
id: SPEC-002
status: APPROVED
feature: sonarqube-integration
created: 2026-03-30
updated: 2026-03-30
author: spec-generator
version: "1.0"
related-specs: []
---

# Spec: Integración de SonarQube en Pipelines CI/CD

> **Estado:** `DRAFT` → aprobar con `status: APPROVED` antes de iniciar implementación.
> **Tipo:** DevOps / Quality Assurance / Infrastructure
> **Impacto:** Ambos proyectos (MVP_FrontEnd + MVP_PetTech)

---

## 1. REQUERIMIENTOS

### Descripción

Integrar SonarCloud (plataforma SaaS gestionada de SonarQube) en los pipelines CI/CD de Frontend y Backend para obtener visibilidad continua de la calidad del código, análisis de vulnerabilidades y deuda técnica. El Quality Gate debe bloquear automáticamente los PRs que no cumplan con métricas mínimas de cobertura y seguridad.

### Problema Resuelto

1. **Sin visibilidad centralizada:** Reportes de cobertura se pierden tras 7 días en artefactos de GitHub Actions.
2. **Sin Quality Gate bloqueante:** Código con baja cobertura o vulnerabilidades llega a `main` sin restricción.
3. **Sin análisis de vulnerabilidades:** Solo lint de estilo; sin detección de OWASP, code smells ni deuda técnica.
4. **Sin historial de evolución:** No existe trazabilidad de métricas por rama o PR.

### Historias de Usuario

#### HU-01: Setup de SonarCloud y Secretos de GitHub

```
Como:        DevOps Engineer / Repository Admin
Quiero:      Crear organización en SonarCloud, generar tokens y configurar secretos en GitHub
Para:        Que el pipeline pueda autenticarse contra SonarCloud sin exponer credenciales

Prioridad:   Alta
Estimación:  M
Dependencias: Ninguna (tarea manual + configuración)
Capa:        DevOps / Infrastructure
```

**Criterios de Aceptación — HU-01**

```gherkin
CRITERIO-1.1: Organización creada en SonarCloud con proyectos pettech_frontend y pettech_backend
  Dado que:  Accedo a https://sonarcloud.io
  Cuando:    Creo organización PetTech con dos proyectos (uno por cada repo/subdirectorio)
  Entonces:  Obtengo SONAR_ORGANIZATION slug (ej. pettech-org) y SONAR_TOKEN

CRITERIO-1.2: Secretos configurados en GitHub Actions
  Dado que:  Tengo SONAR_TOKEN y SONAR_ORGANIZATION
  Cuando:    Accedo a Settings → Secrets and variables → Actions del repo
  Entonces:  Creo los secretos SONAR_TOKEN y SONAR_ORGANIZATION accesibles en los workflows

CRITERIO-1.3: Webhook integrado entre SonarCloud y GitHub
  Dado que:  Los proyectos están creados en SonarCloud
  Cuando:    Configuro el Analysis Results URL (webhook) en SonarCloud
  Entonces:  Los PRs reciben GitHub Checks con resultado del Quality Gate bloqueante
```

#### HU-02: Integración de SonarCloud en Pipeline Frontend

```
Como:        Frontend Developer / QA Engineer
Quiero:      Que el pipeline de Frontend ejecute análisis de SonarCloud tras los tests
Para:        Detectar vulnerabilidades, code smells, bugs y mantener cobertura ≥ 80 %

Prioridad:   Alta
Estimación:  M
Dependencias: HU-01 (secretos configurados)
Capa:        Frontend CI/CD
```

**Criterios de Aceptación — HU-02**

```gherkin
CRITERIO-2.1: Job sonar se ejecuta tras job test en MVP_FrontEnd/.github/workflows/ci.yml
  Dado que:  El job test ha completado exitosamente
  Cuando:    El workflow ejecuta el siguiente job (sonar)
  Entonces:  Se descarga el artefacto coverage-report-frontend y se inicia el análisis de SonarCloud

CRITERIO-2.2: Archivo sonar-project.properties existe en raíz de MVP_FrontEnd
  Dado que:  El job sonar necesita configuración de SonarCloud
  Cuando:    SonarCloud ejecuta el análisis
  Entonces:  Usa MVP_FrontEnd/sonar-project.properties con rutas correctas (src/, coverage/lcov.info)

CRITERIO-2.3: Quality Gate bloquea PR si cobertura < 80 % (nuevo código)
  Dado que:  Un PR tiene cobertura de 78 % en código nuevo
  Cuando:    El Quality Gate evalúa la métrica
  Entonces:  El check "SonarCloud" en el PR falla con estado rojo

CRITERIO-2.4: Quality Gate bloquea PR si tiene vulnerabilidades críticas o altas
  Dado que:  Un PR contiene código vulnerable (OWASP top 10)
  Cuando:    El análisis de SonarCloud detecta la vulnerabilidad
  Entonces:  El check "SonarCloud" falla y bloquea el merge

CRITERIO-2.5: Dashboard de SonarCloud muestra métricas de pettech_frontend
  Dado que:  El análisis completó exitosamente
  Cuando:    Accedo a https://sonarcloud.io/organizations/pettech-org/projects
  Entonces:  Veo el proyecto pettech_frontend con cobertura, bugs, vulnerabilidades y deuda técnica
```

#### HU-03: Integración de SonarCloud en Pipeline Backend

```
Como:        Backend Developer / DevOps Engineer
Quiero:      Que el pipeline de Backend ejecute análisis de SonarCloud tras los tests
Para:        Garantizar código limpio, libre de vulnerabilidades y con cobertura ≥ 80 %

Prioridad:   Alta
Estimación:  M
Dependencias: HU-01 (secretos configurados)
Capa:        Backend CI/CD
```

**Criterios de Aceptación — HU-03**

```gherkin
CRITERIO-3.1: Job sonar se ejecuta tras job test en MVP_PetTech/.github/workflows/ci.yml
  Dado que:  El job test ha completado y generado coverage.xml
  Cuando:    El workflow ejecuta el siguiente job (sonar)
  Entonces:  Se descarga el artefacto coverage-report (JSON de coverage) y se inicia el análisis

CRITERIO-3.2: Job test genera reporte coverage.xml en formato esperado por SonarCloud
  Dado que:  Coverage.py ejecuta con pytest
  Cuando:    Completan los tests
  Entonces:  Se genera coverage.xml en la raíz de MVP_PetTech

CRITERIO-3.3: Archivo sonar-project.properties existe en raíz de MVP_PetTech
  Dado que:  El job sonar necesita configuración
  Cuando:    SonarCloud ejecuta el análisis
  Entonces:  Usa MVP_PetTech/sonar-project.properties con rutas apps/, core/ y coverage.xml

CRITERIO-3.4: Quality Gate bloquea PR si cobertura < 80 % (nuevo código)
  Dado que:  Un PR tiene cobertura de 75 % en código nuevo
  Cuando:    El Quality Gate evalúa la métrica
  Entonces:  El check "SonarCloud" falla y bloquea el merge

CRITERIO-3.5: Quality Gate bloquea PR si tiene vulnerabilidades de seguridad
  Dado que:  Un PR contiene SQL injection o secret hardcodeado
  Cuando:    El análisis de SonarCloud detecta la vulnerabilidad
  Entonces:  El check "SonarCloud" falla con severidad BLOCKER

CRITERIO-3.6: Dashboard de SonarCloud muestra métricas de pettech_backend
  Dado que:  El análisis completó exitosamente
  Cuando:    Acceso a https://sonarcloud.io/organizations/pettech-org/projects
  Entonces:  Veo el proyecto pettech_backend con cobertura Python, bugs, vulnerabilidades y hotspots
```

### Reglas de Negocio (Quality Gate)

1. **Cobertura de líneas (nuevo código):** Mínimo 80 %. Si un PR introduce código nuevo con cobertura < 80 %, el Quality Gate falla.
2. **Duplicación (nuevo código):** Máximo 3 %. Código duplicado > 3 % en cambios nuevos falla el gate.
3. **Vulnerabilidades:** 0 críticas o altas. Cualquier vulnerabilidad de severidad CRITICAL o HIGH bloquea el merge.
4. **Code Smells bloqueantes:** 0 code smells de tipo BLOCKER. Código importante (hotspots) con issues de diseño no debe pasar.
5. **Ciclo de vida del Quality Gate:** Aplica a todo push a `main` y `develop`, y es bloqueante para PRs contra `main`.
6. **Exclusiones de análisis:** Migraciones, archivos de configuración Django, tests unitarios (del análisis de cobertura, pero no de la cobertura en sí) y dist/build deben estar excluidos del análisis de deuda técnica para evitar ruido.

---

## 2. DISEÑO

### Cambios en CI/CD — Pipeline Frontend

#### Archivo: `MVP_FrontEnd/sonar-project.properties` (NUEVO)

```properties
# SonarCloud Configuration — Frontend
sonar.projectKey=pettech_frontend
sonar.projectName=PetTech Frontend
sonar.organization=pettech-org

# Codigo fuente
sonar.sources=src
sonar.exclusions=src/__tests__/**,src/test/**,coverage/**,dist/**,node_modules/**

# Tests y cobertura
sonar.tests=src
sonar.test.inclusions=src/__tests__/**/*.{ts,tsx},src/test/**/*.{ts,tsx}
sonar.typescript.lcov.reportPaths=coverage/lcov.info
sonar.javascript.lcov.reportPaths=coverage/lcov.info

# Excluir tests de la métrica de cobertura
sonar.coverage.exclusions=src/__tests__/**,src/test/**,src/main.tsx,vite.config.ts,**/*.config.ts

# Metadata
sonar.sourceEncoding=UTF-8
```

#### Cambios en Workflow: `MVP_FrontEnd/.github/workflows/ci.yml`

**Agregar nuevo job `sonar` entre el job `test` y el job `build`:**

```yaml
  # ────────────────────────────────────────────────
  # JOB 2.5 — SonarCloud Analysis
  # ────────────────────────────────────────────────
  sonar:
    name: SonarCloud Analysis
    runs-on: ubuntu-latest
    needs: test

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: Download coverage report
        uses: actions/download-artifact@v4
        with:
          name: coverage-report-frontend
          path: coverage/

      - name: Run SonarCloud Analysis
        uses: SonarSource/sonarcloud-github-action@v3
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          args: >
            -Dsonar.projectBaseDir=./MVP_FrontEnd
            -Dsonar.sources=src
            -Dsonar.exclusions=src/__tests__/**,src/test/**,coverage/**,dist/**,node_modules/**
            -Dsonar.tests=src
            -Dsonar.test.inclusions=src/__tests__/**/*.{ts,tsx},src/test/**/*.{ts,tsx}
            -Dsonar.typescript.lcov.reportPaths=coverage/lcov.info
            -Dsonar.coverage.exclusions=src/__tests__/**,src/test/**,src/main.tsx,vite.config.ts
```

---

### Cambios en CI/CD — Pipeline Backend

#### Archivo: `MVP_PetTech/sonar-project.properties` (NUEVO)

```properties
# SonarCloud Configuration — Backend
sonar.projectKey=pettech_backend
sonar.projectName=PetTech Backend
sonar.organization=pettech-org

# Codigo fuente (Python)
sonar.sources=apps,core
sonar.exclusions=**/migrations/**,**/__pycache__/**,**/admin.py,**/apps.py,manage.py,start.py

# Tests
sonar.tests=apps
sonar.test.inclusions=apps/**/tests/**/*.py

# Cobertura (formato XML generado por coverage.py)
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.version=3.12

# Excluir migraciones, admin y config del análisis de cobertura
sonar.coverage.exclusions=**/migrations/**,apps/*/admin.py,apps/*/apps.py,manage.py,start.py,config/**

# Metadata
sonar.sourceEncoding=UTF-8
```

#### Cambios en Workflow: `MVP_PetTech/.github/workflows/ci.yml`

**Modificar el job `test` para generar `coverage.xml`:**

La fase de reportes debe cambiar a:

```yaml
      - name: Generate coverage reports (XML + HTML for SonarCloud)
        run: |
          coverage xml -o coverage.xml \
            --omit="*/migrations/*,*/admin.py,*/apps.py,manage.py,start.py"
          coverage html \
            --omit="*/migrations/*,*/admin.py,*/apps.py,manage.py,start.py"
          coverage report --fail-under=80 \
            --omit="*/migrations/*,*/admin.py,*/apps.py,manage.py,start.py"

      - name: Upload coverage report (with XML)
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report
          path: |
            htmlcov/
            coverage.xml
          retention-days: 7
```

**Agregar nuevo job `sonar` entre el job `test` y el job `build`:**

```yaml
  # ────────────────────────────────────────────────
  # JOB 2.5 — SonarCloud Analysis
  # ────────────────────────────────────────────────
  sonar:
    name: SonarCloud Analysis
    runs-on: ubuntu-latest
    needs: test

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: Download coverage report
        uses: actions/download-artifact@v4
        with:
          name: coverage-report
          path: ./

      - name: Run SonarCloud Analysis
        uses: SonarSource/sonarcloud-github-action@v3
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          args: >
            -Dsonar.projectBaseDir=./MVP_PetTech
            -Dsonar.sources=apps,core
            -Dsonar.exclusions=**/migrations/**,**/__pycache__/**,**/admin.py,**/apps.py,manage.py,start.py
            -Dsonar.tests=apps
            -Dsonar.test.inclusions=apps/**/tests/**/*.py
            -Dsonar.python.coverage.reportPaths=coverage.xml
            -Dsonar.python.version=3.12
            -Dsonar.coverage.exclusions=**/migrations/**,apps/*/admin.py,apps/*/apps.py,manage.py,start.py,config/**
```

---

### Configuración de GitHub y SonarCloud

#### Secretos requeridos en GitHub Actions

Crear los siguientes secretos en **Settings → Secrets and variables → Actions** del repositorio:

| Secreto | Descripción | Valor Ejemplo |
|---------|-------------|---------------|
| `SONAR_TOKEN` | Token de autenticación de SonarCloud | `squ_***` (generado en sonarcloud.io/account/security) |
| `SONAR_ORGANIZATION` | Slug de la organización en SonarCloud | `pettech-org` |

> `GITHUB_TOKEN` ya viene provisto automáticamente por GitHub Actions; no es necesario crear un secreto.
> `SONAR_HOST_URL` no es necesario (por defecto apunta a `https://sonarcloud.io`).

#### Configuración del Webhook en SonarCloud

En la página de Settings del proyecto en SonarCloud:

1. Ir a **Analysis Results → GitHub Checks**.
2. Copiar el URL del webhook proporcionado por SonarCloud.
3. En GitHub repo → Settings → Webhooks, crear un webhook que apunte a ese URL.

---

### Quality Gates en SonarCloud

Para ambos proyectos (`pettech_frontend` y `pettech_backend`), configurar el Quality Gate con las siguientes condiciones:

| Condición | Operador | Umbral | Rama |
|-----------|----------|--------|------|
| Cobertura (nuevo código) | ≥ | 80 % | PR + develop + main |
| Duplicación (nuevo código) | ≤ | 3 % | PR + develop + main |
| Vulnerabilidades | = | 0 (críticas/altas) | PR + develop + main |
| Code Smells bloqueantes | = | 0 (severidad BLOCKER) | PR + develop + main |

---

### Notas de Implementación

1. **Monorepo:** Ambos subcarpetas (MVP_FrontEnd, MVP_PetTech) son proyectos independientes en SonarCloud. No es un análisis único.
2. **Cobertura:** Frontend usa lcov (Vitest + jsdom); Backend usa XML (coverage.py + pytest). Los formatos son distintos por herramientas.
3. **Fetch-depth:** Usar `fetch-depth: 0` en checkout para descargar el historio completo (mejora análisis de hotspots).
4. **Directorios:** Los workflows deben pasar `-Dsonar.projectBaseDir=./` correctamente porque viven en subdirectorios del monorepo.
5. **Tokenización:** El SONAR_TOKEN debe regenerarse cada 12 meses; documentar en README.

---

## 3. LISTA DE TAREAS

> Checklist accionable para todos los agentes (DevOps, Backend, Frontend, QA).
> El Orchestrator monitorea este checklist para determinar el progreso.

### Setup Inicial (DevOps / Repository Admin)

- [ ] Crear cuenta en SonarCloud (https://sonarcloud.io).
- [ ] Crear organización PetTech en SonarCloud y anotar slug (ej. `pettech-org`).
- [ ] Crear dos proyectos: `pettech_frontend` (Key: `pettech_frontend`) y `pettech_backend` (Key: `pettech_backend`).
- [ ] Generar SONAR_TOKEN desde SonarCloud account/security.
- [ ] Crear secreto `SONAR_TOKEN` en GitHub repo Settings → Secrets and variables → Actions.
- [ ] Crear secreto `SONAR_ORGANIZATION` en GitHub repo Settings → Secrets and variables → Actions.
- [ ] Configurar webhook de SonarCloud en GitHub repo → Settings → Webhooks (análisis results → GitHub Checks).
- [ ] Verificar que los dos últimos pushes a `main` ejecutaron el job `sonar` exitosamente.

### Implementación Frontend (Frontend Developer + DevOps)

- [ ] Crear archivo `MVP_FrontEnd/sonar-project.properties` con rutas correctas (src/, coverage/lcov.info).
- [ ] Agregar job `sonar` en `MVP_FrontEnd/.github/workflows/ci.yml` entre `test` y `build`.
- [ ] Job `sonar` descarga artefacto `coverage-report-frontend` antes de ejecutar SonarCloud action.
- [ ] Job `sonar` usa variable `SONAR_TOKEN` y `SONAR_ORGANIZATION` desde GitHub Secrets.
- [ ] Ejecutar un push a `develop` y verificar que el job `sonar` se ejecuta sin errores.
- [ ] Verificar que el proyecto `pettech_frontend` aparece en SonarCloud dashboard.
- [ ] Verificar que métricas (cobertura, bugs, vulnerabilidades) se actualizan correctamente.
- [ ] Crear un PR con cobertura < 80 % y verificar que el Quality Gate falla bloqueante.

### Implementación Backend (Backend Developer + DevOps)

- [ ] Crear archivo `MVP_PetTech/sonar-project.properties` con rutas correctas (apps/, core/, coverage.xml).
- [ ] Modificar job `test` para generar `coverage.xml` además de `coverage.html`.
- [ ] Agregar `coverage.xml` al artefacto `coverage-report` cargado por el job `test`.
- [ ] Agregar job `sonar` en `MVP_PetTech/.github/workflows/ci.yml` entre `test` y `build`.
- [ ] Job `sonar` descarga artefacto `coverage-report` (con coverage.xml) antes de análisis.
- [ ] Job `sonar` usa variable `SONAR_TOKEN` y `SONAR_ORGANIZATION` desde GitHub Secrets.
- [ ] Ejecutar un push a `develop` y verificar que job `sonar` ejecuta sin errores.
- [ ] Verificar que el proyecto `pettech_backend` aparece en SonarCloud dashboard.
- [ ] Verificar que métricas Python (cobertura, bugs, vulnerabilidades) se actualizan correctamente.
- [ ] Crear un PR con vulnerabilidad deliberada y verificar que Quality Gate la detecta y bloquea.

### QA / Verificación (QA Engineer)

- [ ] Documentar Strategy de SonarCloud en `.github/docs/` (URLs, workflows, Quality Gate).
- [ ] Crear matriz de riesgos: vulnerabilidades críticas, code smells bloqueantes, baja cobertura.
- [ ] Validar que PRs con Quality Gate fallido no pueden mergearse a `main` (GitHub branch protection).
- [ ] Validar que Quality Gate permite pasar PR con cobertura = 80.01 % (umbral justo).
- [ ] Validar que Quality Gate bloquea PR con cobertura = 79.99 % (justo por debajo del umbral).
- [ ] Documentar en README.md: cómo consumir reportes de SonarCloud, cómo regenerar tokens, cómo agregar excepciones.

### Documentación (Documentation Agent)

- [ ] Crear documento `sonarcloud-setup.md` en `.github/docs/` con guía de setup inicial.
- [ ] Documentar Quality Gate rules en `.github/docs/qa-guidelines.md`.
- [ ] Crear ADR (Architecture Decision Record) explicando por qué SonarCloud vs self-hosted SonarQube.
- [ ] Actualizar README.md raíz con sección "Code Quality" + enlaces a dashboard de SonarCloud.
- [ ] Documentar cómo regenerar `SONAR_TOKEN` y `SONAR_ORGANIZATION`.

---

## 4. Resumen de Cambios

### Archivos Nuevos
- `MVP_FrontEnd/sonar-project.properties`
- `MVP_PetTech/sonar-project.properties`

### Archivos Modificados
- `MVP_FrontEnd/.github/workflows/ci.yml` — agregar job `sonar`
- `MVP_PetTech/.github/workflows/ci.yml` — agregar job `sonar` + generar coverage.xml

### Configuración de GitHub
- Secreto `SONAR_TOKEN` en repo Settings
- Secreto `SONAR_ORGANIZATION` en repo Settings
- Webhook de SonarCloud en repo Settings (opcional pero recomendado)

### Impacto
- **Tiempo de CI/CD:** +2-3 minutos por pipeline (análisis SonarCloud).
- **Seguridad:** Vulnerabilidades detectadas antes de reach a `main`.
- **Calidad:** Cobertura y deuda técnica visibles en dashboard centralizado.
- **Dev Experience:** Quality Gate bloqueante fuerza disciplina de código limpio.

