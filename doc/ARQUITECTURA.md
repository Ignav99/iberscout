# 🏗️ ARQUITECTURA DEL SISTEMA - IBERSCOUT

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         TU MAC (Local)                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    VISUAL STUDIO CODE                     │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │          research/scrapers_test/               │  │  │
│  │  │  - 01_test_scraper.py                             │  │  │
│  │  │  - 02_besoccer_equipo.py                          │  │  │
│  │  │  - 03_load_to_db.py                               │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              ENTORNO VIRTUAL (.venv)                     │  │
│  │  - Python 3.11+                                          │  │
│  │  - Playwright (navegador automatizado)                   │  │
│  │  - Pandas (manipulación de datos)                        │  │
│  │  - SQLAlchemy (ORM)                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
                               ↓ (HTTP Requests)
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                        FUENTES DE DATOS                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  BeSoccer    │  │ Transfermarkt│  │    FBRef     │        │
│  │              │  │              │  │              │        │
│  │ • Resultados │  │ • Valor $$$  │  │ • Stats xG   │        │
│  │ • Plantillas │  │ • Contratos  │  │ • Métricas   │        │
│  │ • Historial  │  │ • Agencias   │  │ • Advanced   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                               ↓
                               ↓ (Datos Extraídos)
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ZONA DE STAGING (Local)                      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              data/raw/ (CSV, JSON)                       │  │
│  │  - besoccer_equipo_20251119.csv                          │  │
│  │  - transfermarkt_players_20251119.json                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│                    (Limpieza y Transformación)                  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           data/processed/ (CSV limpios)                  │  │
│  │  - players_cleaned.csv                                   │  │
│  │  - teams_normalized.csv                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
                               ↓ (INSERT / UPSERT)
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                   DOCKER CONTAINER (Local)                      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             PostgreSQL 16 (iberscout_db)                 │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────┐    │  │
│  │  │  Schema: research (Investigación)              │    │  │
│  │  │  - players_temp                                │    │  │
│  │  │  - teams_temp                                  │    │  │
│  │  │  - raw_scraping_data (JSONB)                   │    │  │
│  │  └────────────────────────────────────────────────┘    │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────┐    │  │
│  │  │  Schema: production (Futuro)                   │    │  │
│  │  │  - dim_players                                 │    │  │
│  │  │  - dim_teams                                   │    │  │
│  │  │  - fact_matches                                │    │  │
│  │  │  - fact_player_stats                           │    │  │
│  │  └────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Acceso: localhost:5432                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Datos (Data Pipeline)

### FASE 1: EXTRACCIÓN (Extract)
```
[Playwright] → Abre navegador → Navega a BeSoccer
             → Extrae HTML
             → Parse con BeautifulSoup
             → Guarda en data/raw/besoccer_raw.json
```

### FASE 2: TRANSFORMACIÓN (Transform)
```
[Python + Pandas] → Lee data/raw/*.json
                  → Limpia datos (acentos, nulos, duplicados)
                  → Normaliza nombres
                  → Fuzzy Matching (unificar jugadores)
                  → Guarda en data/processed/players_clean.csv
```

### FASE 3: CARGA (Load)
```
[SQLAlchemy] → Lee data/processed/*.csv
             → Conecta a PostgreSQL
             → INSERT (si no existe) o UPDATE (si existe)
             → Verifica integridad referencial
             → Log de operación en logs/
```

---

## 🧩 Módulos del Sistema

### 1. SCRAPING ENGINE
```
research/scrapers_test/
├── base_scraper.py (clase base común)
├── besoccer_scraper.py
├── transfermarkt_scraper.py
└── fbref_scraper.py
```

**Funcionalidades:**
- Rotación de User-Agents
- Delays aleatorios (3-7 seg)
- Manejo de errores y reintentos
- Logging detallado

### 2. DATA PROCESSOR
```
research/processors/
├── cleaner.py (limpieza de datos)
├── matcher.py (fuzzy matching)
└── validator.py (validación con Pydantic)
```

**Funcionalidades:**
- Detección de duplicados
- Normalización de textos
- Conversión de tipos
- Validación de esquemas

### 3. DATABASE LAYER
```
config/
├── settings.py (configuración)
├── db_models.py (modelos SQLAlchemy)
└── db_utils.py (funciones auxiliares)
```

**Funcionalidades:**
- Connection pooling
- Transacciones ACID
- Queries optimizadas
- Migraciones (futuro)

### 4. MONITORING & LOGGING
```
logs/
├── iberscout.log (log general)
├── scraping_errors.log (errores de scraping)
└── db_operations.log (operaciones de BD)
```

**Funcionalidades:**
- Logs estructurados (JSON)
- Rotación de archivos
- Niveles: DEBUG, INFO, WARNING, ERROR

---

## 🔐 Seguridad y Configuración

### Variables de Entorno (.env)
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=iberscout_db
DB_USER=iberscout_user
DB_PASSWORD=<generado automáticamente>

SCRAPING_DELAY_MIN=3
SCRAPING_DELAY_MAX=7
USER_AGENT=Mozilla/5.0...
```

### Docker Compose (docker-compose.yml)
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./data/db:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

---

## 📊 Modelo de Datos (Simplificado)

### Schema: research (temporal)
```sql
-- Tabla para pruebas
CREATE TABLE research.players_temp (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(200),
    position VARCHAR(50),
    age INTEGER,
    nationality VARCHAR(100),
    team VARCHAR(200),
    source VARCHAR(50),
    scraped_at TIMESTAMP
);
```

### Schema: production (futuro)
```sql
-- Jugadores (dimensión)
CREATE TABLE production.dim_players (
    player_id UUID PRIMARY KEY,
    full_name VARCHAR(200),
    birth_date DATE,
    nationality VARCHAR(100),
    position VARCHAR(50)
);

-- Equipos (dimensión)
CREATE TABLE production.dim_teams (
    team_id UUID PRIMARY KEY,
    official_name VARCHAR(200),
    city VARCHAR(100),
    stadium VARCHAR(200)
);

-- Estadísticas (hechos)
CREATE TABLE production.fact_player_stats (
    match_id UUID,
    player_id UUID,
    minutes INTEGER,
    goals INTEGER,
    assists INTEGER,
    xG NUMERIC,
    FOREIGN KEY (player_id) REFERENCES dim_players(player_id)
);
```

---

## 🚀 Evolución del Sistema

### FASE ACTUAL: Investigación
- ✅ Setup del entorno
- ✅ Scrapers básicos
- ⏳ Extracción de 1 equipo
- ⏳ Carga en PostgreSQL

### FASE 2: Escalado (Semanas 2-3)
- Extracción de liga completa
- Fuzzy matching robusto
- Pipeline automatizado
- Dashboard Streamlit básico

### FASE 3: Producción (Mes 2)
- Orquestación con Prefect
- Despliegue en Cloud (Google Cloud Run)
- WebApp pública
- API REST (opcional)

---

## 🛠️ Herramientas de Desarrollo

### Local (Tu Mac)
- Visual Studio Code
- Docker Desktop
- Git

### Python
- Entorno virtual (.venv)
- Pytest (tests)
- Black (formatter)
- Pylint (linter)

### Base de Datos
- PostgreSQL (Docker)
- pgAdmin (opcional, GUI)
- DBeaver (opcional, GUI)

---

## 📈 Métricas de Calidad

### Scraping
- ✅ Tasa de éxito: > 95%
- ✅ Datos completos: > 90%
- ✅ Tiempo de respuesta: < 30s por equipo

### Datos
- ✅ Duplicados: < 2%
- ✅ Valores nulos: < 5%
- ✅ Matching accuracy: > 90%

### Sistema
- ✅ Uptime: 99%
- ✅ Latencia DB: < 100ms
- ✅ Logs sin errores críticos

---

**Última actualización**: 19-Nov-2025  
**Versión de arquitectura**: 1.0.0
