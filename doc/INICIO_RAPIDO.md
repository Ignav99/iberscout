# 🚀 INICIO RÁPIDO - IBERSCOUT

## ⚡ Configuración en 5 minutos

### Opción A: Instalación Automática (Recomendado)

```bash
# 1. Descomprimir el archivo descargado
unzip iberscout_setup.zip
cd iberscout

# 2. Ejecutar script de instalación
chmod +x setup.sh
./setup.sh

# 3. Verificar que todo funciona
source .venv/bin/activate
python verificar_entorno.py

# 4. ¡Listo! Prueba tu primer scraper
python research/scrapers_test/01_test_scraper.py
```

---

### Opción B: Instalación Manual

Si prefieres hacerlo paso a paso, sigue `INSTALACION.md`

---

## 📋 Checklist Rápido

Antes de empezar a programar, verifica:

- [ ] Python 3.11+ instalado
- [ ] Docker Desktop instalado y corriendo
- [ ] Entorno virtual activado (`.venv`)
- [ ] PostgreSQL levantado (`docker ps`)
- [ ] Conexión a DB exitosa (`python research/test_db_connection.py`)

---

## 🗂️ Estructura del Proyecto

```
iberscout/
│
├── 📄 README.md              # Descripción general
├── 📄 INSTALACION.md         # Guía detallada de instalación
├── 📄 PLAN_DE_TRABAJO.md     # Roadmap de desarrollo
├── 📄 INICIO_RAPIDO.md       # Este archivo
│
├── 🔧 setup.sh               # Script de instalación automática
├── 🔧 verificar_entorno.py   # Verificador del entorno
├── 🐳 docker-compose.yml     # Configuración de Docker
│
├── 📁 config/
│   ├── .env.example          # Template de configuración
│   └── settings.py           # Configuración de Python
│
├── 📁 docker/
│   └── init.sql              # Inicialización de PostgreSQL
│
├── 📁 requirements/
│   └── research.txt          # Dependencias Python
│
├── 📁 research/              # ⭐ AQUÍ TRABAJARÁS AHORA
│   ├── notebooks/            # Jupyter notebooks
│   ├── scrapers_test/        # Scripts de prueba
│   ├── data_samples/         # Datos extraídos
│   └── test_db_connection.py # Test de PostgreSQL
│
├── 📁 data/
│   ├── raw/                  # Datos sin procesar
│   ├── processed/            # Datos limpios
│   └── db/                   # Datos de PostgreSQL
│
└── 📁 logs/                  # Archivos de log
```

---

## 🎯 Primeros Pasos

### 1. Familiarízate con las herramientas

```bash
# Ver contenedores Docker corriendo
docker ps

# Ver logs de PostgreSQL
docker-compose logs -f postgres

# Conectar a PostgreSQL directamente
docker exec -it iberscout_postgres psql -U iberscout_user -d iberscout_db
```

### 2. Ejecuta el primer scraper de prueba

```bash
# Asegúrate de que el entorno está activado
source .venv/bin/activate

# Ejecutar scraper de BeSoccer
cd research/scrapers_test
python 01_test_scraper.py
```

**¿Qué esperar?**
- Se abrirá un navegador Chrome
- Navegará a BeSoccer
- Tomará un screenshot
- Guardará datos en `research/data_samples/`

### 3. Abre un Jupyter Notebook (opcional)

```bash
# Iniciar Jupyter
jupyter notebook

# Se abrirá tu navegador en http://localhost:8888
# Navega a: research/notebooks/
```

---

## 🛠️ Comandos Útiles

### Entorno Virtual

```bash
# Activar
source .venv/bin/activate

# Desactivar
deactivate

# Verificar paquetes instalados
pip list
```

### Docker

```bash
# Levantar servicios
docker-compose up -d

# Parar servicios
docker-compose down

# Ver logs
docker-compose logs -f

# Reiniciar solo PostgreSQL
docker-compose restart postgres
```

### Base de Datos

```bash
# Test de conexión
python research/test_db_connection.py

# Conectar con psql
docker exec -it iberscout_postgres psql -U iberscout_user -d iberscout_db

# Ver tablas del schema research
\dt research.*

# Salir de psql
\q
```

### Git (cuando inicialices el repo)

```bash
# Inicializar repositorio
git init

# Primer commit
git add .
git commit -m "Initial commit - Estructura base IberScout"

# Conectar con GitHub (cuando crees el repo)
git remote add origin https://github.com/tu-usuario/iberscout.git
git push -u origin main
```

---

## 📖 Documentación

- **Playwright**: https://playwright.dev/python/docs/intro
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Pandas**: https://pandas.pydata.org/docs/
- **BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

---

## 🆘 Problemas Comunes

### "No such file or directory: .env"
```bash
cp config/.env.example .env
# Edita .env con tus credenciales
```

### "Port 5432 already in use"
```bash
# Parar PostgreSQL local si existe
brew services stop postgresql

# O cambiar el puerto en docker-compose.yml
# ports: "5433:5432"
```

### "playwright: command not found"
```bash
source .venv/bin/activate
pip install playwright
playwright install chromium
```

### "Docker daemon is not running"
```bash
# Abre Docker Desktop desde Aplicaciones
# Espera a que muestre "Docker is running"
```

---

## 📞 Próximos Pasos

1. ✅ Lee `PLAN_DE_TRABAJO.md` para entender el roadmap
2. ✅ Ejecuta `python verificar_entorno.py` para asegurar que todo funciona
3. ✅ Prueba el scraper básico: `python research/scrapers_test/01_test_scraper.py`
4. ✅ Empieza con el Sprint 1: Extracción de un equipo completo

---

**¿Listo?** ¡Manos a la obra! 🚀

**Última actualización**: 19-Nov-2025
