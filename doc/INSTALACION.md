# 🚀 GUÍA DE INSTALACIÓN - IBERSCOUT

Esta guía te llevará paso a paso para configurar el entorno de desarrollo en tu Mac.

## ✅ Pre-requisitos

Antes de empezar, asegúrate de tener instalado:

1. **Python 3.11+**
   ```bash
   python3 --version  # Debería mostrar 3.11 o superior
   ```

2. **Docker Desktop**
   - Descarga desde: https://www.docker.com/products/docker-desktop/
   - Verifica instalación: `docker --version`

3. **Visual Studio Code**
   - Con extensiones recomendadas: Python, Docker, SQLTools

---

## 📁 PASO 1: Crear estructura del proyecto

```bash
# Navega a donde quieras crear el proyecto
cd ~/Documents  # O cualquier carpeta que prefieras

# Crea el directorio principal
mkdir iberscout
cd iberscout

# Crea la estructura de carpetas
mkdir -p research/notebooks research/scrapers_test research/data_samples
mkdir -p src config docker data/raw data/processed data/db logs
mkdir -p requirements

# Abre el proyecto en VS Code
code .
```

---

## 🐍 PASO 2: Configurar entorno virtual Python

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate  # En Mac/Linux
# En Windows sería: .venv\Scripts\activate

# Tu prompt debería mostrar ahora (.venv) al principio
```

---

## 📦 PASO 3: Instalar dependencias

```bash
# Asegúrate de estar en la carpeta iberscout con el entorno activado
pip install --upgrade pip

# Instalar dependencias de investigación
pip install -r requirements/research.txt

# Instalar navegadores de Playwright (obligatorio)
playwright install chromium

# Verificar instalación
pip list | grep playwright
```

---

## 🐳 PASO 4: Configurar variables de entorno

```bash
# Copiar el template de variables de entorno
cp config/.env.example .env

# Editar el archivo .env con tus credenciales
nano .env  # O usar VS Code: code .env
```

**Configuración mínima en `.env`:**
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=iberscout_db
DB_USER=iberscout_user
DB_PASSWORD=TuPasswordSeguro123!  # ⚠️ CAMBIA ESTO
```

---

## 🗄️ PASO 5: Levantar PostgreSQL con Docker

```bash
# Desde la carpeta raíz de iberscout
docker-compose up -d

# Verificar que el contenedor está corriendo
docker ps

# Deberías ver algo como:
# CONTAINER ID   IMAGE                NAMES
# abc123...      postgres:16-alpine   iberscout_postgres

# Ver logs del contenedor (opcional)
docker-compose logs -f postgres
# Presiona Ctrl+C para salir
```

---

## 🧪 PASO 6: Verificar conexión a la base de datos

```bash
# Ejecutar script de prueba
python research/test_db_connection.py

# Si todo va bien, verás:
# ✅ Conexión establecida correctamente
# ✅ TODAS LAS VERIFICACIONES COMPLETADAS
```

---

## 🎉 PASO 7: ¡Listo para empezar!

Si llegaste aquí sin errores, tu entorno está configurado. Ahora puedes:

1. **Abrir un Jupyter Notebook para experimentar:**
   ```bash
   jupyter notebook research/notebooks/
   ```

2. **Crear tu primer scraper de prueba:**
   ```bash
   # Crear archivo de prueba
   touch research/scrapers_test/01_prueba_besoccer.py
   ```

---

## 🔧 Comandos útiles

### Docker
```bash
# Parar contenedores
docker-compose down

# Reiniciar contenedores
docker-compose restart

# Ver logs en tiempo real
docker-compose logs -f

# Limpiar todo (⚠️ BORRA LOS DATOS)
docker-compose down -v
```

### Python
```bash
# Activar entorno virtual
source .venv/bin/activate

# Desactivar entorno virtual
deactivate

# Ver paquetes instalados
pip list

# Actualizar un paquete
pip install --upgrade nombre_paquete
```

### PostgreSQL (desde dentro del contenedor)
```bash
# Conectar a PostgreSQL
docker exec -it iberscout_postgres psql -U iberscout_user -d iberscout_db

# Una vez dentro:
\dt research.*    # Ver tablas del schema research
\q                # Salir
```

---

## 🆘 Solución de problemas

### "Puerto 5432 ya en uso"
```bash
# Ver qué proceso usa el puerto
lsof -i :5432

# Si tienes PostgreSQL instalado localmente, páralo:
brew services stop postgresql
```

### "ModuleNotFoundError"
```bash
# Asegúrate de que el entorno virtual está activado
source .venv/bin/activate

# Reinstala las dependencias
pip install -r requirements/research.txt
```

### "Docker no responde"
```bash
# Reinicia Docker Desktop desde la aplicación
# O desde terminal:
killall Docker && open /Applications/Docker.app
```

---

## 📚 Próximos pasos

Una vez completada la instalación, ve al documento:
`research/notebooks/00_plan_de_trabajo.md`

¡Buena suerte! 🚀
