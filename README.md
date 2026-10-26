## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/[tu-usuario]/[nombre-del-proyecto].git
cd [nombre-del-proyecto]
```

### 2. Crear y activar el entorno virtual

> ⚠️ El entorno se llama **`env`** (no `venv`).

**Windows (CMD):**
```bash
python -m venv env
env\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv env
env\Scripts\Activate.ps1
```

**Git Bash / Linux / macOS:**
```bash
python3 -m venv env
source env/Scripts/activate
```

Debes ver `(env)` al inicio de la terminal. ✅

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
copy .env.example .env      # Windows
cp .env.example .env        # Linux/macOS
```

Edita `.env` con las credenciales reales (pídelas al autor).

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

### 7. Ejecutar el servidor

```bash
python manage.py runserver
```

- 🌐 App: http://127.0.0.1:8000/
- 🔐 Admin: http://127.0.0.1:8000/admin/

---

## 📁 Estructura

```
proyecto/
├── project_core/          # Configuración (settings, urls, wsgi)
├── authentication/        # Login, logout, sesión
├── users/                 # CustomUser
├── dashboard/             # Panel principal
├── core/                  # Utilidades compartidas
├── physiotherapist/       # Fisioterapeutas
├── medical/               # Módulo médico
├── horario/               # Horarios
├── citas/                 # Citas
├── paciente/              # Pacientes
├── expedientes/           # Expedientes clínicos
├── cuestionarios/         # Cuestionarios
├── templates/             # HTML globales
├── static/                # CSS, JS, imágenes globales
├── env/                   # Entorno virtual (NO se sube)
├── .env                   # Variables reales (NO se sube)
├── .env.example           # Plantilla de variables
├── requirements.txt
└── manage.py
```

Cada app contiene su propio `static/`, `templates/`, `models.py`, `views.py`, `urls.py` y `admin.py`.

---

## 🔐 Variables de entorno (`.env`)

```env
SECRET_KEY=tu-clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

FIELD_ENCRYPTION_KEY=tu-clave-fernet

# Supabase PostgreSQL
DB_NAME=postgres
DB_USER=postgres.[project-ref]
DB_PASSWORD=tu-password
DB_HOST=aws-0-sa-east-1.pooler.supabase.com
DB_PORT=5432

# Supabase API y Storage
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_KEY=tu-anon-key
SUPABASE_STORAGE_BUCKET=media
SUPABASE_S3_ACCESS_KEY_ID=tu-access-key
SUPABASE_S3_SECRET_ACCESS_KEY=tu-secret-key
SUPABASE_S3_BUCKET_NAME=media
SUPABASE_S3_REGION_NAME=sa-east-1
SUPABASE_S3_ENDPOINT_URL=https://[project-ref].supabase.co/storage/v1/s3

# Email
EMAIL_USE_TLS=True
EMAIL_PORT=587
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

**Generar claves:**
```bash
# SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# FIELD_ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 🛠️ Comandos útiles

```bash
python manage.py check                 # Verificar configuración
python manage.py makemigrations        # Crear migraciones
python manage.py migrate               # Aplicar migraciones
python manage.py shell                 # Shell interactivo
python manage.py collectstatic         # Recolectar estáticos
python manage.py runserver 8080        # Puerto personalizado
```

---

## 🐛 Problemas comunes

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError: django` | Activa el entorno: `env\Scripts\activate` |
| `KeyError: 'SECRET_KEY'` | Falta el archivo `.env` o la variable |
| `could not connect to server` | Verifica credenciales de Supabase en `.env` |
| CSS/JS no cargan (404) | Confirma `DEBUG=True` y usa `{% load static %}` |
| `Port 8000 already in use` | Usa otro puerto: `runserver 8001` |
| PowerShell bloquea `Activate.ps1` | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |

---

## 📄 Licencia

MIT
