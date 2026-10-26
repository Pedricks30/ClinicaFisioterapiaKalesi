## 💾 Instalación

### 1. Clonar el repositorio
\`\`\`bash
git clone https://github.com/tu-usuario/nombre-del-proyecto.git
cd nombre-del-proyecto
\`\`\`

### 2. Crear el entorno virtual (se llama `env`)
\`\`\`bash
python -m venv env
\`\`\`

### 3. Activar el entorno virtual
**Windows (CMD):**
\`\`\`bash
env\Scripts\activate
\`\`\`

**Windows (PowerShell):**
\`\`\`powershell
env\Scripts\Activate.ps1
\`\`\`

**Linux / macOS / Git Bash:**
\`\`\`bash
source env/Scripts/activate
\`\`\`

> ✅ Debes ver `(env)` al inicio de la terminal.

### 4. Instalar dependencias
\`\`\`bash
pip install --upgrade pip
pip install -r requirements.txt
\`\`\`

### 5. Configurar variables de entorno
\`\`\`bash
cp .env.example .env
\`\`\`
Edita `.env` con las credenciales reales (pídelas al autor del proyecto).

### 6. Aplicar migraciones y correr
\`\`\`bash
python manage.py migrate
python manage.py runserver
\`\`\`
