-- ==========================================
-- IBERSCOUT - INICIALIZACIÓN BASE DE DATOS
-- ==========================================
-- Este script se ejecuta automáticamente cuando se crea el contenedor

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- Para generar UUIDs
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- Para búsquedas de texto difusas

-- Crear schema de investigación (temporal)
CREATE SCHEMA IF NOT EXISTS research;

-- Crear schema de producción (futuro)
CREATE SCHEMA IF NOT EXISTS production;

-- Configurar search_path por defecto
ALTER DATABASE iberscout_db SET search_path TO production, research, public;

-- ===== TABLAS DE INVESTIGACIÓN (TEMPORALES) =====

-- Tabla de prueba para verificar conexión
CREATE TABLE IF NOT EXISTS research.test_connection (
    id SERIAL PRIMARY KEY,
    test_message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO research.test_connection (test_message) 
VALUES ('¡Conexión exitosa desde Docker!');

-- Tabla temporal para almacenar datos crudos de scrapers
CREATE TABLE IF NOT EXISTS research.raw_scraping_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(50) NOT NULL,        -- 'transfermarkt', 'besoccer', etc.
    data_type VARCHAR(50) NOT NULL,     -- 'player', 'team', 'match', etc.
    raw_json JSONB NOT NULL,            -- Datos crudos en JSON
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Índice para búsquedas rápidas por fuente
CREATE INDEX IF NOT EXISTS idx_raw_scraping_source 
ON research.raw_scraping_data(source, data_type);

-- ===== FEEDBACK AL USUARIO =====
DO $$
BEGIN
    RAISE NOTICE '✅ Base de datos IberScout inicializada correctamente';
    RAISE NOTICE '📊 Schemas creados: research, production';
    RAISE NOTICE '🔧 Extensiones: uuid-ossp, pg_trgm';
END $$;
