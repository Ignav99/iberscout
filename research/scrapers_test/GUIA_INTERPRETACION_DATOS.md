# 📖 DOCUMENTACIÓN COMPLETA BASE DE DATOS - IBERSCOUT

> **Archivo único de documentación de BD**
> Se actualiza con cada cambio en la estructura de datos
> Última actualización: Sprint 2/3 - Noviembre 2025

---

## 📋 ÍNDICE

1. [Estado Actual](#-estado-actual)
2. [Estructura de la Tabla](#-estructura-de-la-tabla-researchplayers_temp)
3. [Interpretación de Datos](#-interpretación-de-datos)
4. [Queries SQL por Caso de Uso](#-queries-sql-por-caso-de-uso)
5. [Filtros Útiles](#-filtros-útiles)
6. [Estadísticas Actuales](#-estadísticas-actuales)
7. [Tips para Análisis](#-tips-para-análisis)
8. [Futuras Mejoras](#-futuras-mejoras)

---

## 🎯 ESTADO ACTUAL

### Sprint 2 Completado ✅

- ✅ **110 jugadores cargados** en PostgreSQL
- ✅ **Base de datos operativa** en `research.players_temp`
- ✅ **Datos listos** para Sprint 3 (Fuzzy Matching)

### Próximo Sprint

🔜 **Sprint 3**: Fuzzy Matching - Identificar jugadores duplicados

---

## 🗄️ ESTRUCTURA DE LA TABLA: `research.players_temp`

### Conexión

```bash
Host: localhost
Puerto: 5433
Database: iberscout_db
Schema: research
Tabla: players_temp
```

### Diagrama de Campos

```sql
CREATE TABLE research.players_temp (
    -- Identificación
    id SERIAL PRIMARY KEY,
    dorsal INTEGER,
    nombre VARCHAR(200) NOT NULL,
    posicion VARCHAR(50),

    -- Estadísticas
    partidos_jugados INTEGER DEFAULT 0,
    partidos_titular INTEGER DEFAULT 0,
    goles INTEGER DEFAULT 0,
    asistencias INTEGER DEFAULT 0,

    -- Info personal
    edad INTEGER,

    -- Contexto
    equipo VARCHAR(200),
    liga VARCHAR(100),

    -- Metadatos
    source VARCHAR(50) DEFAULT 'besoccer',
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Descripción de Campos

| Campo | Tipo | Nulable | Descripción | Ejemplo |
|-------|------|---------|-------------|---------|
| **id** | SERIAL | NO | ID único autoincremental | 1, 2, 3... |
| **dorsal** | INTEGER | SÍ | Número de dorsal (0-99) | 10, 7, 1 |
| **nombre** | VARCHAR(200) | NO | Nombre del jugador | "J. Bellingham", "Lionel Messi" |
| **posicion** | VARCHAR(50) | SÍ | Portero, Defensa, Centrocampista, Delantero | "Delantero" |
| **partidos_jugados** | INTEGER | NO | Total de partidos disputados | 14, 8, 0 |
| **partidos_titular** | INTEGER | NO | Partidos como titular | 10, 5, 0 |
| **goles** | INTEGER | NO | ⚠️ Ver sección "Interpretación" | 6, 17, 0 |
| **asistencias** | INTEGER | NO | Asistencias (pases gol) | 4, 2, 0 |
| **edad** | INTEGER | SÍ | Edad del jugador (15-50) | 23, NULL |
| **equipo** | VARCHAR(200) | SÍ | Nombre del equipo | "Real Sociedad B" |
| **liga** | VARCHAR(100) | SÍ | Competición | "3ª RFEF", "Segunda División" |
| **source** | VARCHAR(50) | NO | Fuente de datos | "besoccer" |
| **scraped_at** | TIMESTAMP | NO | Fecha y hora de extracción | 2025-11-19 21:13:15 |

### Constraints (Validaciones)

```sql
-- Edad válida
CONSTRAINT check_edad_valida
    CHECK (edad IS NULL OR (edad >= 15 AND edad <= 50))

-- Dorsal válido
CONSTRAINT check_dorsal_valido
    CHECK (dorsal IS NULL OR (dorsal >= 0 AND dorsal <= 99))

-- Estadísticas no negativas
CONSTRAINT check_stats_positivas CHECK (
    partidos_jugados >= 0 AND
    partidos_titular >= 0 AND
    goles >= 0 AND
    asistencias >= 0
)
```

### Índices (Para búsquedas rápidas)

```sql
CREATE INDEX idx_players_temp_equipo ON research.players_temp(equipo);
CREATE INDEX idx_players_temp_liga ON research.players_temp(liga);
CREATE INDEX idx_players_temp_posicion ON research.players_temp(posicion);
CREATE INDEX idx_players_temp_nombre ON research.players_temp(nombre);
```

**Ventaja**: Las queries con `WHERE equipo = '...'` o `WHERE liga = '...'` son más rápidas.

---

## ⚠️ IMPORTANTE: Interpretación de la columna "goles"

### 🧤 Para PORTEROS

La columna `goles` representa **GOLES ENCAJADOS** (goles en contra), no goles marcados.

**Ejemplo**:
```
Aitor Fraga (Portero) - 17 goles = 17 goles encajados en 11 partidos
```

### ⚽ Para JUGADORES DE CAMPO

La columna `goles` representa **GOLES MARCADOS** (goles a favor).

**Ejemplo**:
```
C. Fernández (Delantero) - 6 goles = 6 goles marcados en 12 partidos
```

---

## 📝 QUERIES SQL POR CASO DE USO

### 🏆 RANKINGS Y TOP

#### Top 10 Goleadores (sin porteros)

```sql
SELECT nombre, equipo, posicion, goles
FROM research.players_temp
WHERE posicion != 'Portero'
ORDER BY goles DESC
LIMIT 10;
```

**Resultado esperado**:
```
I. Alayeto    | Tudelano    | Delantero | 6 goles
C. Fernández  | CD Mirandés | Delantero | 6 goles
T. Bouguettaya| Tudelano    | Delantero | 4 goles
```

---

#### Top 10 Asistentes

```sql
SELECT nombre, equipo, posicion, asistencias, partidos_jugados
FROM research.players_temp
WHERE asistencias > 0
ORDER BY asistencias DESC
LIMIT 10;
```

---

#### Jugadores más participativos (goles + asistencias)

```sql
SELECT
    nombre,
    equipo,
    posicion,
    goles,
    asistencias,
    (goles + asistencias) as participaciones,
    partidos_jugados
FROM research.players_temp
WHERE posicion != 'Portero'
ORDER BY (goles + asistencias) DESC
LIMIT 10;
```

---

### 🧤 PORTEROS

#### Porteros menos goleados

```sql
SELECT
    nombre,
    equipo,
    goles as goles_encajados,
    partidos_jugados
FROM research.players_temp
WHERE posicion = 'Portero' AND partidos_jugados > 0
ORDER BY goles ASC
LIMIT 5;
```

**Interpretación**:
```
Pol (Utebo) - 5 goles encajados en 3 partidos = 1.67 goles/partido
```

---

### 🏟️ ANÁLISIS POR EQUIPO

#### Plantilla completa de un equipo

```sql
SELECT
    dorsal,
    nombre,
    posicion,
    edad,
    partidos_jugados,
    goles,
    asistencias
FROM research.players_temp
WHERE equipo = 'Real Sociedad B'
ORDER BY
    CASE posicion
        WHEN 'Portero' THEN 1
        WHEN 'Defensa' THEN 2
        WHEN 'Centrocampista' THEN 3
        WHEN 'Delantero' THEN 4
    END,
    dorsal;
```

---

#### Comparar equipos (estadísticas)

```sql
SELECT
    equipo,
    liga,
    COUNT(*) as total_jugadores,
    ROUND(AVG(edad), 1) as edad_promedio,
    SUM(CASE WHEN posicion != 'Portero' THEN goles ELSE 0 END) as goles_equipo,
    SUM(asistencias) as asistencias_equipo
FROM research.players_temp
GROUP BY equipo, liga
ORDER BY goles_equipo DESC;
```

---

#### Top goleador por equipo

```sql
WITH ranked AS (
    SELECT
        equipo,
        nombre,
        posicion,
        goles,
        ROW_NUMBER() OVER (PARTITION BY equipo ORDER BY goles DESC) as rank
    FROM research.players_temp
    WHERE posicion != 'Portero'
)
SELECT equipo, nombre, posicion, goles
FROM ranked
WHERE rank = 1
ORDER BY goles DESC;
```

---

### 📊 ESTADÍSTICAS GENERALES

#### Jugadores por posición con estadísticas

```sql
SELECT
    posicion,
    COUNT(*) as total_jugadores,
    ROUND(AVG(edad), 1) as edad_promedio,
    SUM(CASE WHEN posicion != 'Portero' THEN goles ELSE 0 END) as total_goles_marcados,
    SUM(CASE WHEN posicion = 'Portero' THEN goles ELSE 0 END) as total_goles_encajados
FROM research.players_temp
GROUP BY posicion
ORDER BY total_jugadores DESC;
```

---

#### Distribución de edad por posición

```sql
SELECT
    posicion,
    COUNT(*) as total,
    ROUND(AVG(edad), 1) as edad_promedio,
    MIN(edad) as edad_min,
    MAX(edad) as edad_max
FROM research.players_temp
WHERE edad IS NOT NULL
GROUP BY posicion
ORDER BY edad_promedio;
```

---

### 🔍 BÚSQUEDAS Y FILTROS AVANZADOS

#### Buscar jugador por nombre (parcial)

```sql
SELECT nombre, equipo, posicion, edad, partidos_jugados
FROM research.players_temp
WHERE nombre ILIKE '%bellingham%'
ORDER BY nombre;
```

**Nota**: `ILIKE` es case-insensitive (no distingue mayúsculas).

---

#### Jugadores jóvenes prometedores (sub-23 con minutos)

```sql
SELECT
    nombre,
    equipo,
    edad,
    posicion,
    partidos_jugados,
    goles,
    asistencias
FROM research.players_temp
WHERE
    edad <= 23
    AND posicion != 'Portero'
    AND partidos_jugados >= 5
ORDER BY (goles + asistencias) DESC;
```

---

#### Jugadores sin minutos (posibles salidas)

```sql
SELECT nombre, equipo, posicion, edad, dorsal
FROM research.players_temp
WHERE partidos_jugados = 0
ORDER BY equipo, posicion;
```

---

#### Jugadores titulares fijos (>70% de partidos como titular)

```sql
SELECT
    nombre,
    equipo,
    posicion,
    partidos_jugados,
    partidos_titular,
    ROUND((partidos_titular::DECIMAL / NULLIF(partidos_jugados, 0)) * 100, 1) as porcentaje_titular
FROM research.players_temp
WHERE partidos_jugados >= 5
    AND (partidos_titular::DECIMAL / partidos_jugados) >= 0.7
ORDER BY porcentaje_titular DESC;
```

---

### 🎯 CASOS DE USO SCOUTING

#### Delanteros con mejor ratio gol/partido

```sql
SELECT
    nombre,
    equipo,
    edad,
    goles,
    partidos_jugados,
    ROUND(goles::DECIMAL / NULLIF(partidos_jugados, 0), 2) as ratio_gol_partido
FROM research.players_temp
WHERE
    posicion = 'Delantero'
    AND partidos_jugados >= 5
ORDER BY ratio_gol_partido DESC
LIMIT 10;
```

---

#### Centrocampistas creativos (asistencias)

```sql
SELECT
    nombre,
    equipo,
    edad,
    asistencias,
    partidos_jugados,
    ROUND(asistencias::DECIMAL / NULLIF(partidos_jugados, 0), 2) as ratio_asist_partido
FROM research.players_temp
WHERE
    posicion = 'Centrocampista'
    AND partidos_jugados >= 5
    AND asistencias > 0
ORDER BY ratio_asist_partido DESC;
```

---

#### Defensas goleadores (poco común, valioso)

```sql
SELECT nombre, equipo, edad, goles, partidos_jugados
FROM research.players_temp
WHERE posicion = 'Defensa' AND goles > 0
ORDER BY goles DESC;
```

---

### ⏱️ JUGADORES ACTIVOS

#### Jugadores más activos (partidos jugados)

```sql
SELECT nombre, equipo, posicion, partidos_jugados, partidos_titular
FROM research.players_temp
ORDER BY partidos_jugados DESC
LIMIT 10;
```

---

## 🔍 FILTROS ÚTILES

### Por equipo
```sql
WHERE equipo = 'Real Sociedad B'
```

### Por liga
```sql
WHERE liga = '3ª RFEF'
```

### Por rango de edad
```sql
WHERE edad BETWEEN 18 AND 23
```

### Sin valores NULL en edad
```sql
WHERE edad IS NOT NULL
```

### Solo jugadores con minutos
```sql
WHERE partidos_jugados > 0
```

---

## 📊 ESTADÍSTICAS ACTUALES

**Datos en BD** (Sprint 2 - Noviembre 2025):

- **Total jugadores**: 110
- **Equipos**: 4 (CD Mirandés, Real Sociedad B, Tudelano, Utebo)
- **Ligas**: Segunda División, 1ª RFEF, 2ª RFEF, 3ª RFEF
- **Edad promedio**: 22.9 años
- **Jugadores sin edad**: 3 (con NULL)

**Distribución por posición**:
- Defensa: 35 (31.8%)
- Delantero: 33 (30.0%)
- Centrocampista: 29 (26.4%)
- Portero: 13 (11.8%)

---

## 🚀 FUTURAS MEJORAS (Post-Sprint 5)

Si en producción se requiere mayor claridad, se puede:

### Opción A: Dos columnas separadas
```sql
ALTER TABLE players ADD COLUMN goles_encajados INTEGER DEFAULT 0;
-- Migrar datos existentes
UPDATE players SET goles_encajados = goles WHERE posicion = 'Portero';
UPDATE players SET goles = 0 WHERE posicion = 'Portero';
```

### Opción B: Tablas por posición
```sql
CREATE TABLE goalkeeper_stats (
    player_id INT,
    goles_encajados INT,
    paradas INT,
    clean_sheets INT
);

CREATE TABLE field_player_stats (
    player_id INT,
    goles INT,
    asistencias INT,
    tiros INT
);
```

**Por ahora**: Queries con filtros son suficientes para fase de investigación.

---

## 💡 TIPS PARA ANÁLISIS

1. **Siempre filtrar porteros** cuando busques goleadores
2. **Usar CASE** para diferenciar en agregaciones
3. **Documentar** en dashboards que "goles porteros = encajados"
4. **Normalizar por partidos jugados** (goles/partido) para comparar

---

---

## 📞 ROADMAP

### Completado ✅
- ✅ Sprint 0: Setup técnico
- ✅ Sprint 1: Extracción piloto (4 equipos)
- ✅ Sprint 2: Carga en PostgreSQL (110 jugadores)

### En progreso 🔄
- 🔄 Sprint 3: Fuzzy Matching

### Pendiente 🔜
- 🔜 Sprint 4: Extracción masiva (liga completa ~500 jugadores)
- 🔜 Sprint 5: Análisis exploratorio con Jupyter

---

## 📝 HISTORIAL DE CAMBIOS

### v1.1 - Sprint 2/3 (Noviembre 2025)
- ✅ Expandida documentación completa de BD
- ✅ Agregada estructura de tabla con todos los campos
- ✅ 30+ queries SQL por caso de uso
- ✅ Secciones: Rankings, Porteros, Equipos, Búsquedas, Scouting
- ✅ Documentación de constraints e índices

### v1.0 - Sprint 2 (Noviembre 2025)
- ✅ Creación inicial del archivo
- ✅ Documentación de interpretación de "goles"
- ✅ Queries básicas
- ✅ 110 jugadores cargados

---

**Última actualización**: Sprint 2/3 - Noviembre 2025
**Autor**: Proyecto IberScout
**Archivo único**: Actualizar aquí con cada cambio en la estructura de datos
