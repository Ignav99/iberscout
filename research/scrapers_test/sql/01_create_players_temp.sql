-- ==========================================
-- SPRINT 2: Crear tabla temporal de jugadores
-- ==========================================
-- Tabla para almacenar datos extraídos de BeSoccer
-- Schema: research (para investigación)

-- Conectar a la base de datos
\c iberscout_db

-- Crear tabla si no existe
CREATE TABLE IF NOT EXISTS research.players_temp (
    id SERIAL PRIMARY KEY,
    dorsal INTEGER,
    nombre VARCHAR(200) NOT NULL,
    posicion VARCHAR(50),
    partidos_jugados INTEGER DEFAULT 0,
    partidos_titular INTEGER DEFAULT 0,
    goles INTEGER DEFAULT 0,
    asistencias INTEGER DEFAULT 0,
    edad INTEGER,
    equipo VARCHAR(200),
    liga VARCHAR(100),
    source VARCHAR(50) DEFAULT 'besoccer',
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT check_edad_valida CHECK (edad IS NULL OR (edad >= 15 AND edad <= 50)),
    CONSTRAINT check_dorsal_valido CHECK (dorsal IS NULL OR (dorsal >= 0 AND dorsal <= 99)),
    CONSTRAINT check_stats_positivas CHECK (
        partidos_jugados >= 0 AND
        partidos_titular >= 0 AND
        goles >= 0 AND
        asistencias >= 0
    )
);

-- Crear índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_players_temp_equipo ON research.players_temp(equipo);
CREATE INDEX IF NOT EXISTS idx_players_temp_liga ON research.players_temp(liga);
CREATE INDEX IF NOT EXISTS idx_players_temp_posicion ON research.players_temp(posicion);
CREATE INDEX IF NOT EXISTS idx_players_temp_nombre ON research.players_temp(nombre);

-- Comentarios para documentación
COMMENT ON TABLE research.players_temp IS 'Tabla temporal para datos de jugadores extraídos durante fase de investigación';
COMMENT ON COLUMN research.players_temp.dorsal IS 'Número de dorsal del jugador (0-99)';
COMMENT ON COLUMN research.players_temp.nombre IS 'Nombre del jugador tal como aparece en BeSoccer';
COMMENT ON COLUMN research.players_temp.posicion IS 'Posición: Portero, Defensa, Centrocampista, Delantero';
COMMENT ON COLUMN research.players_temp.source IS 'Fuente de datos (besoccer, transfermarkt, fbref)';

-- Mostrar estructura de la tabla
\d research.players_temp

-- Contar registros actuales
SELECT COUNT(*) as total_jugadores FROM research.players_temp;
