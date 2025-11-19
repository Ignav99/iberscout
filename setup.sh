#!/bin/bash

# ==========================================
# IBERSCOUT - SCRIPT DE INSTALACIÓN AUTOMÁTICA
# ==========================================
# Este script configura automáticamente el entorno en tu Mac

set -e  # Detener si hay algún error

echo ""
echo "======================================================================"
echo "  🏆 IBERSCOUT - INSTALACIÓN AUTOMÁTICA"
echo "======================================================================"
echo ""

# Verificar que estamos en Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  Este script está diseñado para macOS"
    echo "Si estás en Linux, los comandos son similares"
    echo ""
    read -p "¿Deseas continuar de todas formas? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# ===== 1. VERIFICAR PYTHON =====
echo "🔍 Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✅ Python $PYTHON_VERSION encontrado"
else
    echo "❌ Python 3 no está instalado"
    echo "💡 Instálalo desde: https://www.python.org/downloads/"
    exit 1
fi

# ===== 2. VERIFICAR DOCKER =====
echo ""
echo "🔍 Verificando Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker instalado"
    
    if docker ps &> /dev/null; then
        echo "✅ Docker está corriendo"
    else
        echo "⚠️  Docker no está corriendo"
        echo "💡 Abre Docker Desktop desde Aplicaciones"
        exit 1
    fi
else
    echo "❌ Docker no está instalado"
    echo "💡 Descárgalo desde: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# ===== 3. CREAR ESTRUCTURA DE DIRECTORIOS =====
echo ""
echo "📁 Creando estructura de directorios..."

mkdir -p research/notebooks
mkdir -p research/scrapers_test
mkdir -p research/data_samples
mkdir -p src
mkdir -p config
mkdir -p docker
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/db
mkdir -p logs
mkdir -p requirements

echo "✅ Directorios creados"

# ===== 4. MOVER ARCHIVOS A SUS UBICACIONES =====
echo ""
echo "🔧 Organizando archivos..."

# Mover archivos de config
if [ -f "env_example.txt" ]; then
    mv env_example.txt config/.env.example
    echo "✅ config/.env.example"
fi

if [ -f "settings.py" ]; then
    mv settings.py config/settings.py
    echo "✅ config/settings.py"
fi

# Mover archivos de Docker
if [ -f "init.sql" ]; then
    mv init.sql docker/init.sql
    echo "✅ docker/init.sql"
fi

# Mover archivos de requirements
if [ -f "requirements_research.txt" ]; then
    mv requirements_research.txt requirements/research.txt
    echo "✅ requirements/research.txt"
fi

# Mover scripts de test
if [ -f "test_db_connection.py" ]; then
    mv test_db_connection.py research/test_db_connection.py
    echo "✅ research/test_db_connection.py"
fi

if [ -f "01_test_scraper.py" ]; then
    mv 01_test_scraper.py research/scrapers_test/01_test_scraper.py
    echo "✅ research/scrapers_test/01_test_scraper.py"
fi

# Mover .gitignore
if [ -f "gitignore.txt" ]; then
    mv gitignore.txt .gitignore
    echo "✅ .gitignore"
fi

# ===== 5. CREAR ENTORNO VIRTUAL =====
echo ""
echo "🐍 Creando entorno virtual Python..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Entorno virtual creado"
else
    echo "⚠️  El entorno virtual ya existe"
fi

# ===== 6. ACTIVAR ENTORNO E INSTALAR DEPENDENCIAS =====
echo ""
echo "📦 Instalando dependencias..."
echo "⏳ Esto puede tardar 2-3 minutos..."

source .venv/bin/activate

pip install --upgrade pip --quiet
pip install -r requirements/research.txt --quiet

echo "✅ Dependencias instaladas"

# ===== 7. INSTALAR NAVEGADORES PLAYWRIGHT =====
echo ""
echo "🌐 Instalando navegadores de Playwright..."
echo "⏳ Primera vez: Puede tardar 3-5 minutos descargando Chromium..."

playwright install chromium --quiet

echo "✅ Chromium instalado"

# ===== 8. CREAR ARCHIVO .ENV =====
echo ""
echo "⚙️  Configurando variables de entorno..."

if [ ! -f ".env" ]; then
    cp config/.env.example .env
    
    # Generar password aleatorio
    RANDOM_PASSWORD=$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 20)
    
    # Reemplazar password en .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/changeme_secure_password/$RANDOM_PASSWORD/" .env
        sed -i '' "s/cambiar_password_seguro/$RANDOM_PASSWORD/" .env
    else
        sed -i "s/changeme_secure_password/$RANDOM_PASSWORD/" .env
        sed -i "s/cambiar_password_seguro/$RANDOM_PASSWORD/" .env
    fi
    
    echo "✅ Archivo .env creado con password seguro"
else
    echo "⚠️  El archivo .env ya existe (no se sobrescribió)"
fi

# ===== 9. LEVANTAR POSTGRESQL CON DOCKER =====
echo ""
echo "🐳 Levantando PostgreSQL con Docker..."

docker-compose up -d

echo "⏳ Esperando a que PostgreSQL inicie (10 segundos)..."
sleep 10

echo "✅ PostgreSQL corriendo"

# ===== 10. VERIFICAR CONEXIÓN =====
echo ""
echo "🧪 Verificando conexión a base de datos..."

python research/test_db_connection.py

# ===== FINALIZADO =====
echo ""
echo "======================================================================"
echo "  ✅ ¡INSTALACIÓN COMPLETADA!"
echo "======================================================================"
echo ""
echo "📚 PRÓXIMOS PASOS:"
echo ""
echo "1. Activa el entorno virtual (si no lo está):"
echo "   source .venv/bin/activate"
echo ""
echo "2. Ejecuta el verificador completo:"
echo "   python verificar_entorno.py"
echo ""
echo "3. Lee el plan de trabajo:"
echo "   cat PLAN_DE_TRABAJO.md"
echo ""
echo "4. Prueba tu primer scraper:"
echo "   python research/scrapers_test/01_test_scraper.py"
echo ""
echo "======================================================================"
echo ""
