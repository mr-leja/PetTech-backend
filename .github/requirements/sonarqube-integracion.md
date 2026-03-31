# Requerimiento: Integración de SonarQube en los Pipelines CI/CD

## Descripción General

Actualmente los pipelines de CI/CD de `MVP_FrontEnd` y `MVP_PetTech` ejecutan lint, tests con cobertura y build, pero los resultados de calidad de código (cobertura, duplicados, code smells, vulnerabilidades) no se publican en ninguna plataforma centralizada. Se requiere integrar **SonarQube Cloud** (SonarCloud) en ambos pipelines para obtener visibilidad continua de la calidad del código y bloquear merges que no superen los Quality Gates definidos.

## Problema / Necesidad

1. **Sin visibilidad central de calidad:** Los reportes de cobertura se suben como artefactos temporales de GitHub Actions (7 días) pero no hay dashboard persistente ni histórico de métricas.
2. **Sin análisis estático unificado:** Flake8 y TypeScript type-check solo detectan errores de estilo/tipos; no hay análisis de vulnerabilidades (OWASP), code smells ni deuda técnica con umbrales bloqueantes.
3. **Sin Quality Gate que bloquee el merge:** Actualmente no existe ningún mecanismo automático que impida que código con baja cobertura o vulnerabilidades críticas llegue a `main`.
4. **Falta de trazabilidad:** No existe historial de evolución de métricas por rama ni por PR en las dos aplicaciones del monorepo.

## Solución Propuesta

Integrar **SonarCloud** (SaaS gestionado, sin servidor self-hosted) en el paso posterior a `test` en ambos pipelines, pasando los reportes de cobertura ya generados.

---

### 1. Pipeline Frontend — `MVP_FrontEnd/.github/workflows/ci.yml`

#### 1.1 Archivo de configuración `MVP_FrontEnd/sonar-project.properties`

```properties
sonar.projectKey=pettech_frontend
sonar.projectName=PetTech Frontend
sonar.sources=src
sonar.exclusions=src/__tests__/**,src/test/**,coverage/**,dist/**,node_modules/**
sonar.tests=src
sonar.test.inclusions=src/__tests__/**/*.{ts,tsx},src/test/**/*.{ts,tsx}
sonar.typescript.lcov.reportPaths=coverage/lcov.info
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.coverage.exclusions=src/__tests__/**,src/test/**,src/main.tsx,vite.config.ts
```

#### 1.2 Nuevo JOB `sonar` en el pipeline Frontend

- **Posición:** después del job `test`, antes del job `build`.
- **Dependencia:** `needs: test`.
- **Acción usada:** `SonarSource/sonarcloud-github-action@v3`.
- **Directorio de trabajo:** `./MVP_FrontEnd` (el action debe apuntar al subdirectorio correcto dado que el workflow vive en `MVP_FrontEnd/.github/workflows/`).
- El job debe descargar el artefacto `coverage-report-frontend` (subido en el job `test`) antes de correr el análisis, para que SonarCloud reciba el `lcov.info`.

#### 1.3 Quality Gate Frontend

| Métrica | Umbral bloqueante |
|---------|------------------|
| Cobertura de líneas (nuevo código) | ≥ 80 % |
| Duplicación (nuevo código) | ≤ 3 % |
| Vulnerabilidades críticas/altas | 0 |
| Code smells bloqueantes | 0 |

---

### 2. Pipeline Backend — `MVP_PetTech/.github/workflows/ci.yml`

#### 2.1 Archivo de configuración `MVP_PetTech/sonar-project.properties`

```properties
sonar.projectKey=pettech_backend
sonar.projectName=PetTech Backend
sonar.sources=apps,core
sonar.exclusions=**/migrations/**,**/__pycache__/**,**/admin.py,**/apps.py,manage.py,start.py
sonar.tests=apps
sonar.test.inclusions=apps/**/tests/**/*.py
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.version=3.12
sonar.coverage.exclusions=**/migrations/**,apps/*/admin.py,apps/*/apps.py,manage.py,start.py,config/**
```

#### 2.2 Ajuste al job `test` del pipeline Backend

El comando de cobertura debe generar adicionalmente un reporte en formato XML (requerido por SonarCloud para Python):

```yaml
- name: Run tests with coverage (XML + HTML)
  run: |
    coverage run -m pytest apps/ \
      --ignore=apps/adopciones/migrations \
      --ignore=apps/mascotas/migrations \
      --ignore=apps/familias/migrations \
      --ignore=apps/usuarios/migrations \
      -v --tb=short

- name: Generate coverage reports
  run: |
    coverage xml -o coverage.xml \
      --omit="*/migrations/*,*/admin.py,*/apps.py,manage.py,start.py"
    coverage html \
      --omit="*/migrations/*,*/admin.py,*/apps.py,manage.py,start.py"
    coverage report --fail-under=80 \
      --omit="*/migrations/*,*/admin.py,*/apps.py,manage.py,start.py"
```

El artefacto `coverage-report` debe incluir también el `coverage.xml` para que el job `sonar` pueda descargarlo.

#### 2.3 Nuevo JOB `sonar` en el pipeline Backend

- **Posición:** después del job `test`, antes del job `build`.
- **Dependencia:** `needs: test`.
- **Acción usada:** `SonarSource/sonarcloud-github-action@v3`.
- **Directorio de trabajo:** `./MVP_PetTech`.
- El job debe descargar el artefacto `coverage-report` antes del análisis.

#### 2.4 Quality Gate Backend

| Métrica | Umbral bloqueante |
|---------|------------------|
| Cobertura de líneas (nuevo código) | ≥ 80 % |
| Duplicación (nuevo código) | ≤ 3 % |
| Vulnerabilidades críticas/altas | 0 |
| Code smells bloqueantes | 0 |

---

### 3. Secretos de GitHub requeridos

Los siguientes secretos deben configurarse en **Settings → Secrets and variables → Actions** del repositorio:

| Secreto | Descripción | Scope |
|---------|-------------|-------|
| `SONAR_TOKEN` | Token de autenticación de SonarCloud (generado en sonarcloud.io) | Repositorio |
| `SONAR_ORGANIZATION` | Slug de la organización en SonarCloud | Repositorio |

> **Nota:** `SONAR_HOST_URL` no es necesario al usar SonarCloud (se usa `https://sonarcloud.io` por defecto).

---

### 4. Restricción de ramas con Quality Gate

En SonarCloud debe configurarse para los proyectos `pettech_frontend` y `pettech_backend`:

- **Branch principal:** `main`
- **Ramas de análisis:** `main`, `develop` y cualquier PR contra `main` o `develop`
- El webhook de SonarCloud debe integrarse con GitHub para que el Quality Gate bloquee los PRs como GitHub Check.

---

### 5. Archivos afectados

| Archivo | Cambio | Proyecto |
|---------|--------|----------|
| `MVP_FrontEnd/.github/workflows/ci.yml` | Agregar JOB `sonar` entre `test` y `build` | Frontend |
| `MVP_FrontEnd/sonar-project.properties` | Crear archivo nuevo | Frontend |
| `MVP_PetTech/.github/workflows/ci.yml` | Agregar JOB `sonar` entre `test` y `build`; ajustar generación de `coverage.xml` | Backend |
| `MVP_PetTech/sonar-project.properties` | Crear archivo nuevo | Backend |

---

### 6. Criterios de Aceptación

- [ ] El job `sonar` se ejecuta en ambos pipelines tras el job `test` en pushes a `main` y `develop`.
- [ ] El análisis de SonarCloud recibe el reporte de cobertura correcto en cada proyecto (lcov para frontend, XML para backend).
- [ ] Ambos proyectos aparecen en el dashboard de SonarCloud con métricas visibles.
- [ ] Un PR con cobertura < 80 % en nuevo código falla el Quality Gate y bloquea el merge.
- [ ] Un PR con vulnerabilidades críticas falla el Quality Gate y bloquea el merge.
- [ ] Los archivos de configuración `sonar-project.properties` excluyen migraciones, tests y archivos de configuración del análisis de cobertura.
- [ ] Las variables secretas (`SONAR_TOKEN`, `SONAR_ORGANIZATION`) están documentadas en el README del repositorio.
