"""
==========================================
IBERSCOUT - CONFIGURACIÓN CENTRALIZADA
==========================================
Gestión de variables de entorno y configuración del proyecto
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
    print(f"✅ Variables de entorno cargadas desde {ENV_FILE}")
else:
    print(f"⚠️  Archivo .env no encontrado. Usando valores por defecto.")
    print(f"💡 Copia 'config/.env.example' a '.env' y configúralo.")


# ===== CONFIGURACIÓN DE BASE DE DATOS =====
class DatabaseConfig:
    HOST = os.getenv("DB_HOST", "localhost")
    PORT = int(os.getenv("DB_PORT", 5432))
    NAME = os.getenv("DB_NAME", "iberscout_db")
    USER = os.getenv("DB_USER", "iberscout_user")
    PASSWORD = os.getenv("DB_PASSWORD", "changeme_secure_password")
    
    @classmethod
    def get_connection_string(cls):
        """Genera la cadena de conexión para PostgreSQL"""
        return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.NAME}"
    
    @classmethod
    def get_sqlalchemy_uri(cls):
        """URI compatible con SQLAlchemy"""
        return f"postgresql+psycopg2://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.NAME}"


# ===== CONFIGURACIÓN DE SCRAPING =====
class ScrapingConfig:
    DELAY_MIN = float(os.getenv("SCRAPING_DELAY_MIN", 3))
    DELAY_MAX = float(os.getenv("SCRAPING_DELAY_MAX", 7))
    USER_AGENT = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    TIMEOUT = 30  # Timeout en segundos para requests


# ===== RUTAS DEL PROYECTO =====
class PathsConfig:
    BASE_DIR = BASE_DIR
    DATA_DIR = BASE_DIR / "data"
    DATA_RAW = DATA_DIR / "raw"
    DATA_PROCESSED = DATA_DIR / "processed"
    DATA_DB = DATA_DIR / "db"
    LOGS_DIR = BASE_DIR / "logs"
    RESEARCH_DIR = BASE_DIR / "research"
    
    @classmethod
    def create_directories(cls):
        """Crea todos los directorios necesarios si no existen"""
        directories = [
            cls.DATA_RAW,
            cls.DATA_PROCESSED,
            cls.DATA_DB,
            cls.LOGS_DIR,
            cls.RESEARCH_DIR / "notebooks",
            cls.RESEARCH_DIR / "scrapers_test",
            cls.RESEARCH_DIR / "data_samples"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Estructura de directorios verificada")


# ===== LOGGING =====
class LoggingConfig:
    LEVEL = os.getenv("LOG_LEVEL", "INFO")
    FILE = BASE_DIR / "logs" / "iberscout.log"


# ===== FUENTES DE DATOS =====
class DataSourcesConfig:
    TRANSFERMARKT_BASE_URL = "https://www.transfermarkt.es"
    BESOCCER_BASE_URL = "https://www.besoccer.com"
    FBREF_BASE_URL = "https://fbref.com"
    RFEF_BASE_URL = "https://www.rfef.es"


# Ejecutar al importar el módulo
if __name__ == "__main__":
    print("\n" + "="*50)
    print("CONFIGURACIÓN DE IBERSCOUT")
    print("="*50)
    print(f"Base de datos: {DatabaseConfig.HOST}:{DatabaseConfig.PORT}/{DatabaseConfig.NAME}")
    print(f"Directorio base: {PathsConfig.BASE_DIR}")
    print(f"Nivel de log: {LoggingConfig.LEVEL}")
    print("="*50 + "\n")
    
    # Crear directorios
    PathsConfig.create_directories()
