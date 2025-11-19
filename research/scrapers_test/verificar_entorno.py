#!/usr/bin/env python3
"""
==========================================
IBERSCOUT - VERIFICACIÓN COMPLETA DEL ENTORNO
==========================================
Este script verifica que todos los componentes están instalados y configurados correctamente
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Imprime un encabezado bonito"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def print_success(text):
    """Mensaje de éxito"""
    print(f"✅ {text}")


def print_error(text):
    """Mensaje de error"""
    print(f"❌ {text}")


def print_warning(text):
    """Mensaje de advertencia"""
    print(f"⚠️  {text}")


def check_python_version():
    """Verifica la versión de Python"""
    print_header("1. VERIFICANDO PYTHON")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"📍 Python version: {version_str}")
    
    if version.major >= 3 and version.minor >= 11:
        print_success("Python 3.11+ detectado")
        return True
    else:
        print_error(f"Se requiere Python 3.11+, tienes {version_str}")
        return False


def check_virtual_env():
    """Verifica que estamos en un entorno virtual"""
    print_header("2. VERIFICANDO ENTORNO VIRTUAL")
    
    if sys.prefix != sys.base_prefix:
        print_success("Entorno virtual activado")
        print(f"📍 Ubicación: {sys.prefix}")
        return True
    else:
        print_warning("No estás en un entorno virtual")
        print("💡 Ejecuta: source .venv/bin/activate")
        return False


def check_dependencies():
    """Verifica que las dependencias principales están instaladas"""
    print_header("3. VERIFICANDO DEPENDENCIAS")
    
    required_packages = [
        "playwright",
        "beautifulsoup4",
        "pandas",
        "psycopg2",
        "sqlalchemy",
        "thefuzz",
        "python-dotenv"
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - NO INSTALADO")
            missing.append(package)
    
    if missing:
        print("\n💡 Instala las dependencias faltantes:")
        print("   pip install -r requirements/research.txt")
        return False
    
    return True


def check_playwright_browsers():
    """Verifica que los navegadores de Playwright están instalados"""
    print_header("4. VERIFICANDO NAVEGADORES PLAYWRIGHT")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print_success("Chromium instalado y funcional")
                return True
            except Exception as e:
                print_error(f"Chromium no disponible: {e}")
                print("💡 Ejecuta: playwright install chromium")
                return False
                
    except ImportError:
        print_error("Playwright no está instalado")
        return False


def check_docker():
    """Verifica que Docker está corriendo"""
    print_header("5. VERIFICANDO DOCKER")
    
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print_success("Docker está corriendo")
            
            # Verificar contenedor de PostgreSQL
            if "iberscout_postgres" in result.stdout:
                print_success("Contenedor PostgreSQL detectado")
                return True
            else:
                print_warning("Contenedor PostgreSQL no está corriendo")
                print("💡 Ejecuta: docker-compose up -d")
                return False
        else:
            print_error("Docker no está disponible")
            return False
            
    except FileNotFoundError:
        print_error("Docker no está instalado")
        return False


def check_database_connection():
    """Verifica la conexión a PostgreSQL"""
    print_header("6. VERIFICANDO CONEXIÓN A POSTGRESQL")
    
    try:
        import psycopg2
        from config.settings import DatabaseConfig
        
        conn = psycopg2.connect(
            host=DatabaseConfig.HOST,
            port=DatabaseConfig.PORT,
            database=DatabaseConfig.NAME,
            user=DatabaseConfig.USER,
            password=DatabaseConfig.PASSWORD,
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print_success("Conexión establecida")
        print(f"📍 {version.split(',')[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"No se pudo conectar: {e}")
        print("💡 Verifica que el contenedor esté corriendo: docker ps")
        return False


def check_directory_structure():
    """Verifica que la estructura de directorios existe"""
    print_header("7. VERIFICANDO ESTRUCTURA DE DIRECTORIOS")
    
    required_dirs = [
        "research/notebooks",
        "research/scrapers_test",
        "research/data_samples",
        "data/raw",
        "data/processed",
        "data/db",
        "logs",
        "config"
    ]
    
    all_exist = True
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print_success(f"{dir_path}/")
        else:
            print_error(f"{dir_path}/ - NO EXISTE")
            all_exist = False
    
    if not all_exist:
        print("\n💡 Ejecuta el script de configuración para crear directorios")
    
    return all_exist


def check_env_file():
    """Verifica que existe el archivo .env"""
    print_header("8. VERIFICANDO ARCHIVO .ENV")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print_success(".env encontrado")
        
        # Verificar que no tenga valores por defecto peligrosos
        content = env_file.read_text()
        
        if "changeme" in content.lower() or "cambiar" in content.lower():
            print_warning("El archivo .env contiene passwords por defecto")
            print("💡 Actualiza las credenciales en .env")
            return False
        
        return True
    else:
        print_warning(".env no encontrado")
        print("💡 Copia config/.env.example a .env y configúralo")
        return False


def main():
    """Función principal"""
    print("\n" + "🚀 "*30)
    print("VERIFICACIÓN COMPLETA DEL ENTORNO - IBERSCOUT")
    print("🚀 "*30)
    
    checks = [
        ("Python", check_python_version),
        ("Entorno Virtual", check_virtual_env),
        ("Dependencias", check_dependencies),
        ("Playwright", check_playwright_browsers),
        ("Docker", check_docker),
        ("PostgreSQL", check_database_connection),
        ("Directorios", check_directory_structure),
        ("Configuración", check_env_file)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Error inesperado en {name}: {e}")
            results.append((name, False))
    
    # Resumen final
    print_header("RESUMEN DE VERIFICACIÓN")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"📊 Verificaciones completadas: {passed}/{total}\n")
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print("🎉 ¡TODO LISTO! Tu entorno está correctamente configurado.")
        print("📚 Próximo paso: Lee research/PLAN_DE_TRABAJO.md")
        print("="*60 + "\n")
        return 0
    else:
        print("⚠️  Hay componentes que requieren atención.")
        print("📖 Revisa INSTALACION.md para más detalles")
        print("="*60 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
