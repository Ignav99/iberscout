-- ==========================================
-- SPRINT 5: Crear tabla DEFINITIVA de jugadores (v1)
-- ==========================================
-- Tabla con datos extendidos de BeSoccer (plantilla + fichas individuales)
-- Schema: research (para investigación)
--
-- NUEVOS CAMPOS vs players_temp:
--   - temporada (para multi-temporada)
--   - minutos_jugados (desde fichas individuales)
--   - pie_dominante (desde fichas individuales)
--   - nacionalidad (desde fichas individuales, opcional)

-- Conectar a la base de datos
\c iberscout_db

-- Crear tabla si no existe
CREATE TABLE IF NOT EXISTS research.players (
    id SERIAL PRIMARY KEY,

    -- ========================================
    -- CORE: Identificación del jugador
    -- ========================================
    nombre VARCHAR(200) NOT NULL,
    dorsal INTEGER,
    posicion VARCHAR(50),
    edad INTEGER,
    equipo VARCHAR(200) NOT NULL,
    liga VARCHAR(100) NOT NULL,
    temporada VARCHAR(10) NOT NULL,  -- '2024/25', '2023/24', etc.

    -- ========================================
    -- ESTADÍSTICAS BÁSICAS (desde tabla plantilla)
    -- ========================================
    partidos_jugados INTEGER DEFAULT 0,
    partidos_titular INTEGER DEFAULT 0,
    goles INTEGER DEFAULT 0,
    asistencias INTEGER DEFAULT 0,

    -- ========================================
    -- ESTADÍSTICAS EXTENDIDAS (desde ficha individual)
    -- ========================================
    minutos_jugados INTEGER,           -- NUEVO: Minutos totales jugados
    pie_dominante VARCHAR(20),         -- NUEVO: 'Derecho', 'Izquierdo', 'Ambidiestro'
    nacionalidad VARCHAR(50),          -- NUEVO: España, otros (opcional)

    -- ========================================
    -- METADATA
    -- ========================================
    source VARCHAR(50) DEFAULT 'besoccer',
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- ========================================
    -- CONSTRAINTS
    -- ========================================
    CONSTRAINT check_edad_valida CHECK (edad IS NULL OR (edad >= 15 AND edad <= 50)),
    CONSTRAINT check_dorsal_valido CHECK (dorsal IS NULL OR (dorsal >= 0 AND dorsal <= 99)),
    CONSTRAINT check_stats_positivas CHECK (
        partidos_jugados >= 0 AND
        partidos_titular >= 0 AND
        goles >= 0 AND
        asistencias >= 0
    ),
    CONSTRAINT check_minutos_validos CHECK (minutos_jugados IS NULL OR minutos_jugados >= 0),
    CONSTRAINT check_pie_valido CHECK (pie_dominante IS NULL OR pie_dominante IN ('Derecho', 'Izquierdo', 'Ambidiestro'))
);

-- ========================================
-- ÍNDICES para búsquedas rápidas
-- ========================================
CREATE INDEX IF NOT EXISTS idx_players_equipo ON research.players(equipo);
CREATE INDEX IF NOT EXISTS idx_players_liga ON research.players(liga);
CREATE INDEX IF NOT EXISTS idx_players_temporada ON research.players(temporada);
CREATE INDEX IF NOT EXISTS idx_players_posicion ON research.players(posicion);
CREATE INDEX IF NOT EXISTS idx_players_nombre ON research.players(nombre);
CREATE INDEX IF NOT EXISTS idx_players_liga_temporada ON research.players(liga, temporada);

-- ========================================
-- COMENTARIOS para documentación
-- ========================================
COMMENT ON TABLE research.players IS 'Tabla definitiva v1 - Jugadores con datos extendidos (plantilla + fichas individuales BeSoccer)';

-- Campos core
COMMENT ON COLUMN research.players.nombre IS 'Nombre del jugador tal como aparece en BeSoccer';
COMMENT ON COLUMN research.players.dorsal IS 'Número de dorsal (0-99)';
COMMENT ON COLUMN research.players.posicion IS 'Posición: Portero, Defensa, Centrocampista, Delantero';
COMMENT ON COLUMN research.players.edad IS 'Edad del jugador al momento de extracción';
COMMENT ON COLUMN research.players.equipo IS 'Nombre del equipo';
COMMENT ON COLUMN research.players.liga IS 'Liga: 3ª RFEF, 2ª RFEF, 1ª RFEF, etc.';
COMMENT ON COLUMN research.players.temporada IS 'Temporada: 2024/25, 2023/24, 2022/23';

-- Estadísticas básicas
COMMENT ON COLUMN research.players.partidos_jugados IS 'Total partidos jugados (titular + suplente)';
COMMENT ON COLUMN research.players.partidos_titular IS 'Partidos como titular';
COMMENT ON COLUMN research.players.goles IS 'Goles marcados (para porteros = goles encajados)';
COMMENT ON COLUMN research.players.asistencias IS 'Asistencias realizadas';

-- Estadísticas extendidas
COMMENT ON COLUMN research.players.minutos_jugados IS 'Minutos totales jugados (desde ficha individual)';
COMMENT ON COLUMN research.players.pie_dominante IS 'Pie dominante: Derecho, Izquierdo, Ambidiestro';
COMMENT ON COLUMN research.players.nacionalidad IS 'Nacionalidad del jugador (si disponible)';

-- Metadata
COMMENT ON COLUMN research.players.source IS 'Fuente de datos: besoccer, transfermarkt, fbref';
COMMENT ON COLUMN research.players.scraped_at IS 'Timestamp de extracción';

-- ========================================
-- MOSTRAR estructura
-- ========================================
\d research.players

-- ========================================
-- CONSULTAS DE VALIDACIÓN
-- ========================================
SELECT COUNT(*) as total_jugadores FROM research.players;
SELECT liga, temporada, COUNT(*) as jugadores
FROM research.players
GROUP BY liga, temporada
ORDER BY liga, temporada;
