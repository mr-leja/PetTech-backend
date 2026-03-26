# PetTech Backend

API REST con Django 5, Clean Architecture, JWT y PostgreSQL.

## Stack
- Python 3.12, Django 5, Django REST Framework
- PostgreSQL 16
- Almacenamiento de imágenes: Amazon S3 (producción) / filesystem local (desarrollo)
- JWT via `djangorestframework-simplejwt`
- Podman / podman-compose

## Estructura
```
apps/
  usuarios/    # Custom User, JWT, roles (ADMIN/FAMILIA)
  mascotas/    # Registro y gestión de mascotas
  familias/    # Registro de familias y condiciones del hogar
config/        # Configuración Django (base/development/production)
core/          # Utilidades: permisos, paginación, excepciones
start.py       # Script de arranque embebido en la imagen (espera DB + migrate)
```

---

## Inicio rápido con Podman

### 1. Clonar y preparar
```bash
git clone https://github.com/mr-leja/PetTech-backend.git
cd PetTech-backend
```

### 2. Levantar por primera vez
```bash
podman-compose up --build
```

El backend espera automáticamente a que PostgreSQL esté listo, aplica las migraciones y crea el **admin por defecto**.

### 3. Arranques posteriores (sin rebuild)
```bash
podman-compose up
```

### 4. Detener
```bash
podman-compose down
```

### 5. Detener y borrar volúmenes (reset total de la BD)
```bash
podman-compose down -v
```

### 6. Ver logs en tiempo real
```bash
podman logs -f pettech_backend
podman logs -f pettech_db
```

---

## Admin por defecto

Al ejecutar `podman-compose up --build` por primera vez, el sistema crea automáticamente:

| Campo | Valor |
|-------|-------|
| Email | `admin@pettech.com` |
| Contraseña | `Admin1234!` |
| Rol | `ADMIN` |

### Verificar que funciona (PowerShell)
```powershell
Invoke-WebRequest "http://localhost:8000/api/v1/auth/login/" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"admin@pettech.com","password":"Admin1234!"}' `
  -UseBasicParsing | Select-Object StatusCode
# Esperado: StatusCode 200
```

### Verificar que funciona (curl / bash)
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@pettech.com","password":"Admin1234!"}' | python -m json.tool
```

### Crear un admin adicional manualmente
```bash
podman exec -it pettech_backend python manage.py shell -c "
from apps.usuarios.infrastructure.models import Usuario
Usuario.objects.create_superuser(
    email='otro_admin@pettech.com',
    password='OtraPass123!',
    nombre='Segundo Admin',
    rol='ADMIN'
)
print('Admin creado.')
"
```

### Cambiar la contraseña del admin por defecto
```bash
podman exec -it pettech_backend python manage.py shell -c "
from apps.usuarios.infrastructure.models import Usuario
u = Usuario.objects.get(email='admin@pettech.com')
u.set_password('NuevaContraseña123!')
u.save()
print('Contraseña actualizada.')
"
```

---

## Ejecutar migraciones manualmente
Necesario solo si agregaste nuevos modelos:
```bash
podman exec pettech_backend python manage.py makemigrations
podman exec pettech_backend python manage.py migrate
```

---

## Endpoints principales
| Método | URL | Acceso | Descripción |
|--------|-----|--------|-------------|
| POST | `/api/v1/auth/login/` | Público | Login — retorna JWT |
| POST | `/api/v1/auth/registro/` | Público | Registro nuevo usuario FAMILIA |
| GET  | `/api/v1/auth/perfil/` | Autenticado | Perfil del usuario actual |
| POST | `/api/v1/auth/token/refresh/` | Autenticado | Renovar access token |
| GET  | `/api/v1/mascotas/` | Autenticado | Listar mascotas (filtros: `?estado=` `?especie=`) |
| POST | `/api/v1/mascotas/` | Solo ADMIN | Registrar mascota |
| GET  | `/api/v1/mascotas/{id}/` | Autenticado | Detalle mascota |
| PATCH| `/api/v1/mascotas/{id}/` | Solo ADMIN | Editar mascota |
| DELETE| `/api/v1/mascotas/{id}/` | Solo ADMIN | Eliminar mascota |
| POST | `/api/v1/familias/mia/` | FAMILIA | Registrar datos de familia (HU-04) |
| GET  | `/api/v1/familias/mia/` | FAMILIA | Ver mi familia |
| POST | `/api/v1/familias/mia/condiciones-hogar/` | FAMILIA | Registrar hogar + acuerdo (HU-05) |
| GET  | `/api/v1/familias/` | Solo ADMIN | Listar todas las familias |

---

## Desarrollo local (sin Podman)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements/development.txt

# Necesitas PostgreSQL local corriendo con:
# DB: pettech, USER: pettech_user, PASSWORD: pettech_password

python manage.py migrate
python manage.py runserver
```

---

## Almacenamiento de imágenes con Amazon S3

Las fotos de mascotas y los carnets de vacunas pueden almacenarse en S3.  
Por defecto (`USE_S3=False`) se usa el sistema de archivos local (carpeta `media/`).

### Activar S3

1. **Crear el bucket** en AWS (p. ej. `pettech-fotos`) en la región deseada.
2. Habilitar acceso público de lectura para los objetos del bucket (o usar CloudFront).
3. Crear un usuario IAM con política `AmazonS3FullAccess` (o política mínima sobre ese bucket) y obtener `Access Key ID` y `Secret Access Key`.
4. Copiar `.env.example` a `.env` y completar las variables:

```env
USE_S3=True
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=pettech-fotos
# Dominio personalizado (CloudFront u otro CDN) — opcional
AWS_S3_CUSTOM_DOMAIN=
```

5. Reiniciar el servidor. Las imágenes nuevas se subirán automáticamente a S3.  
   Las imágenes guardadas localmente **no** se migran automáticamente; deben subirse al bucket manualmente si es necesario.

### Variables de entorno S3

| Variable | Descripción | Requerida con USE_S3=True |
|---|---|---|
| `USE_S3` | Activa (`True`) o desactiva (`False`) S3 | Siempre |
| `AWS_ACCESS_KEY_ID` | Clave de acceso IAM | Sí |
| `AWS_SECRET_ACCESS_KEY` | Clave secreta IAM | Sí |
| `AWS_REGION` | Región del bucket (ej. `us-east-1`) | Sí |
| `AWS_S3_BUCKET_NAME` | Nombre del bucket | Sí |
| `AWS_S3_CUSTOM_DOMAIN` | CDN / dominio personalizado | No |
| `AWS_S3_ENDPOINT_URL` | Endpoint alternativo (p. ej. MinIO local) | No |
