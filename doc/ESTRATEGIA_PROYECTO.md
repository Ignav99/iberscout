# 🎯 ESTRATEGIA DEL PROYECTO IBERSCOUT

**Versión:** 1.0
**Fecha:** 20 Noviembre 2025
**Objetivo:** Sistema de scouting completo para fútbol español de categorías inferiores

---

## 📋 VISIÓN GENERAL

IberScout es una base de datos de scouting que recopila estadísticas de jugadores de las categorías inferiores del fútbol español, con el objetivo de identificar talento en divisiones donde hay menos cobertura mediática.

### Categorías objetivo (en orden de desarrollo):
1. ✅ **3ª RFEF** (18 grupos, ~360 equipos, ~9000 jugadores/temporada)
2. **División de Honor Juvenil** (menos datos disponibles)
3. **2ª RFEF** (4 grupos, ~80 equipos, ~2000 jugadores/temporada)
4. **1ª RFEF** (2 grupos, ~40 equipos, ~1000 jugadores/temporada)
5. **2ª División** (22 equipos, ~550 jugadores/temporada)

### Temporadas objetivo:
- 2024/25 (actual)
- 2023/24
- 2022/23
- Posible extensión a temporadas anteriores según necesidad

---

## 🎯 FILOSOFÍA DE DESARROLLO: LIGA POR LIGA

### Principio fundamental:
**NO mezclar todas las ligas a la vez. Perfeccionar una liga antes de pasar a la siguiente.**

### Por qué:
1. Cada liga tiene **diferentes fuentes de datos disponibles**
2. Cada liga puede tener **diferentes métricas accesibles**
3. Las páginas web tienen **estructuras HTML diferentes**
4. Diferentes ligas requieren **scripts específicos**

### Flujo de trabajo por liga:

```
┌─────────────────────────────────────────────────────────┐
│ FASE 1: INVESTIGACIÓN Y PROTOTIPO                      │
├─────────────────────────────────────────────────────────┤
│ 1. Identificar fuentes de datos disponibles            │
│    (BeSoccer, LaPreferente, FutbolMe, Transfermarkt)   │
│                                                         │
│ 2. Explorar QUÉ datos concretos se pueden extraer      │
│    (partidos, goles, minutos, tarjetas, altura, etc.)  │
│                                                         │
│ 3. Crear script de prueba con 1 EQUIPO                 │
│    - Validar extracción                                │
│    - Verificar calidad de datos                        │
│    - Ajustar columnas de BD según disponibilidad       │
│                                                         │
│ 4. Documentar estructura y métricas en                 │
│    GUIA_INTERPRETACION_DATOS.md                        │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│ FASE 2: VALIDACIÓN                                     │
├─────────────────────────────────────────────────────────┤
│ 1. Revisar datos del equipo de prueba                  │
│    - Estadísticas coherentes                           │
│    - No hay errores de parseo                          │
│    - Campos correctamente mapeados                     │
│                                                         │
│ 2. Probar con 2-3 equipos más                          │
│    - Confirmar consistencia                            │
│    - Detectar casos especiales                         │
│                                                         │
│ 3. Ajustar script según hallazgos                      │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│ FASE 3: EXTRACCIÓN MASIVA                              │
├─────────────────────────────────────────────────────────┤
│ 1. LIMPIAR base de datos (TRUNCATE)                    │
│                                                         │
│ 2. Ejecutar extracción completa                        │
│    - Todos los equipos                                 │
│    - Todas las temporadas                              │
│    - Una sola ejecución (sin duplicados)               │
│                                                         │
│ 3. Cargar a PostgreSQL                                 │
│                                                         │
│ 4. Fuzzy matching (solo si hay múltiples cargas)       │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│ FASE 4: SIGUIENTE LIGA                                 │
├─────────────────────────────────────────────────────────┤
│ Repetir el ciclo completo con la siguiente liga        │
└─────────────────────────────────────────────────────────┘
```

---

## 🗄️ DISEÑO DE BASE DE DATOS

### Estrategia elegida: **TABLA ÚNICA CON COLUMNAS NULLABLE**

#### Ventajas:
- ✅ Todo centralizado en `research.players`
- ✅ Queries simples sin JOINs complejos
- ✅ Fácil comparar jugadores entre ligas
- ✅ Escalable: agregar columnas según descubrimos nuevas fuentes
- ✅ PostgreSQL gestiona bien las columnas NULL (no ocupan espacio)

#### Estructura propuesta:

```sql
CREATE TABLE research.players (
    -- ========================================
    -- CORE: Obligatorio para todas las ligas
    -- ========================================
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    posicion VARCHAR(50) NOT NULL,
    equipo VARCHAR(100) NOT NULL,
    liga VARCHAR(50) NOT NULL,              -- '3ª RFEF', '2ª RFEF', '1ª RFEF', etc.
    temporada VARCHAR(10) NOT NULL,          -- '2024/25', '2023/24', etc.

    fecha_extraccion TIMESTAMP DEFAULT NOW(),
    fuente_datos VARCHAR(50),                -- 'BeSoccer', 'LaPreferente', etc.

    -- ========================================
    -- BÁSICO: Disponible en la mayoría de ligas
    -- ========================================
    dorsal INT,
    edad INT,
    partidos_jugados INT DEFAULT 0,
    partidos_titular INT DEFAULT 0,
    goles INT DEFAULT 0,
    asistencias INT DEFAULT 0,

    -- ========================================
    -- EXTENDIDO: Solo algunas ligas
    -- ========================================
    minutos_jugados INT,                     -- Disponibilidad: por determinar
    tarjetas_amarillas INT,                  -- Disponibilidad: por determinar
    tarjetas_rojas INT,                      -- Disponibilidad: por determinar

    nacionalidad VARCHAR(50),                -- Solo ligas superiores
    altura INT,                              -- Solo algunas fuentes (cm)
    peso INT,                                -- Solo algunas fuentes (kg)
    pie_dominante VARCHAR(20),               -- 'Derecho', 'Izquierdo', 'Ambidiestro'

    valor_mercado INT,                       -- Solo 2ª División, 1ª RFEF, 2ª RFEF

    -- ========================================
    -- AVANZADO: Solo ligas premium con datos detallados
    -- ========================================
    xG DECIMAL(5,2),                         -- Expected Goals (FBRef/StatsBomb)
    xA DECIMAL(5,2),                         -- Expected Assists
    pases_completados INT,
    precision_pases DECIMAL(5,2),
    duelos_ganados INT,
    duelos_totales INT,
    recuperaciones INT,
    intercepciones INT,

    -- ========================================
    -- METADATA
    -- ========================================
    CONSTRAINT chk_edad CHECK (edad IS NULL OR (edad >= 15 AND edad <= 50)),
    CONSTRAINT chk_dorsal CHECK (dorsal IS NULL OR (dorsal >= 0 AND dorsal <= 99)),
    CONSTRAINT chk_stats_positive CHECK (
        partidos_jugados >= 0 AND
        partidos_titular >= 0 AND
        goles >= 0 AND
        asistencias >= 0
    )
);

-- Índices para búsquedas rápidas
CREATE INDEX idx_players_liga ON research.players(liga);
CREATE INDEX idx_players_temporada ON research.players(temporada);
CREATE INDEX idx_players_equipo ON research.players(equipo);
CREATE INDEX idx_players_posicion ON research.players(posicion);
CREATE INDEX idx_players_nombre ON research.players(nombre);
CREATE INDEX idx_players_liga_temporada ON research.players(liga, temporada);
```

### Gestión de columnas NULL:

**En `GUIA_INTERPRETACION_DATOS.md` documentaremos:**

| Columna | 3ª RFEF | Div Honor Juv | 2ª RFEF | 1ª RFEF | 2ª Div |
|---------|---------|---------------|---------|---------|--------|
| dorsal | ✅ | ✅ | ✅ | ✅ | ✅ |
| edad | ✅ | ✅ | ✅ | ✅ | ✅ |
| partidos_jugados | ✅ | ✅ | ✅ | ✅ | ✅ |
| goles | ✅ | ✅ | ✅ | ✅ | ✅ |
| minutos_jugados | ❓ | ❓ | ❓ | ✅ | ✅ |
| tarjetas | ❓ | ❓ | ❓ | ✅ | ✅ |
| altura | ❌ | ❌ | ❓ | ✅ | ✅ |
| valor_mercado | ❌ | ❌ | ✅ | ✅ | ✅ |
| xG | ❌ | ❌ | ❌ | ❌ | ✅ |

**Leyenda:**
- ✅ = Disponible y confirmado
- ❓ = Por investigar
- ❌ = No disponible

---

## 📊 FUENTES DE DATOS POR LIGA

### 3ª RFEF:
| Fuente | Estado | Datos disponibles |
|--------|--------|-------------------|
| **BeSoccer** | ✅ Validado | Plantillas, partidos, goles, asistencias, edad |
| **LaPreferente** | 🔍 Por explorar | Estadísticas, goleadores, histórico |
| **FutbolMe** | 🔍 Por explorar | Resultados, goleadores, tarjetas |
| **Transfermarkt** | ❌ No disponible | N/A |

### División de Honor Juvenil:
| Fuente | Estado | Datos disponibles |
|--------|--------|-------------------|
| Por investigar | 🔍 | - |

### 2ª RFEF:
| Fuente | Estado | Datos disponibles |
|--------|--------|-------------------|
| **BeSoccer** | 🔍 Por explorar | Similar a 3ª RFEF |
| **Transfermarkt** | ❓ Por confirmar | Posiblemente valor de mercado |

### 1ª RFEF:
| Fuente | Estado | Datos disponibles |
|--------|--------|-------------------|
| **BeSoccer** | 🔍 Por explorar | Estadísticas completas |
| **Transfermarkt** | ✅ Disponible | Valor mercado, transferencias |

### 2ª División:
| Fuente | Estado | Datos disponibles |
|--------|--------|-------------------|
| **BeSoccer** | 🔍 Por explorar | Estadísticas completas |
| **Transfermarkt** | ✅ Disponible | Valor mercado, transferencias, histórico |
| **FBRef** | ✅ Disponible | Métricas avanzadas (xG, pases, etc.) |

---

## 🚀 PLAN DE SPRINTS

### ✅ Sprint 0: Setup (COMPLETADO)
- Configuración entorno Python
- PostgreSQL en Docker
- Playwright + Firefox
- Scripts básicos

### ✅ Sprint 1-2: Scraping básico (COMPLETADO)
- Script `02_analisis_liga.py` funcional
- Extracción de 4 equipos (110 jugadores)
- Carga a PostgreSQL

### ✅ Sprint 3: Fuzzy Matching (COMPLETADO)
- POC con 19 casos de prueba
- Algoritmo óptimo: partial_ratio 70%
- Script aplicado a BD

### ✅ Sprint 4: Extracción automática (COMPLETADO)
- `extraer_equipos_liga.py` - Captura equipos automáticamente
- `06_extraccion_liga_completa.py` - Scraping masivo
- Validado con 18 equipos, 472 jugadores

---

### 🔄 Sprint 5: PERFECCIONAR 3ª RFEF (EN CURSO)

**Objetivo:** Maximizar datos de 3ª RFEF antes de extracción masiva definitiva

#### Tareas:

1. **Investigar BeSoccer más a fondo**
   - ¿Las fichas individuales de jugadores tienen más datos?
   - ¿Hay minutos jugados, tarjetas, altura, peso, nacionalidad?
   - Probar con 1 jugador específico

2. **Explorar LaPreferente.com**
   - Crear script de prueba con Playwright
   - Extraer 1 equipo de prueba
   - Comparar datos con BeSoccer
   - Identificar métricas adicionales disponibles

3. **Explorar FutbolMe**
   - Similar a LaPreferente
   - Evaluar si aporta datos únicos

4. **Actualizar esquema de BD**
   - Agregar columnas según datos disponibles
   - Actualizar constraints
   - Regenerar `01_create_players_temp.sql`

5. **Probar extracción enriquecida con 1 equipo**
   - Combinar datos de múltiples fuentes si es necesario
   - Validar calidad
   - Documentar en `GUIA_INTERPRETACION_DATOS.md`

6. **Crear script de extracción multi-temporada**
   - `07_extraccion_3rfef_completa.py`
   - Parametrizable por temporada
   - Extrae los 18 grupos
   - Output: ~9000 jugadores × 3 temporadas = ~27,000 registros

7. **Crear script de limpieza de BD**
   - `reset_database.py`
   - TRUNCATE + reset secuencias
   - Ejecutar ANTES de extracción definitiva

8. **Extracción definitiva 3ª RFEF**
   - Limpiar BD
   - Extraer 2024/25, 2023/24, 2022/23
   - Cargar todo
   - Validar (NO fuzzy matching porque es extracción única)

---

### 🔮 Sprint 6: División de Honor Juvenil

1. Investigar fuentes disponibles
2. Probar con 1 equipo
3. Crear script específico
4. Extracción masiva
5. Cargar a BD

---

### 🔮 Sprint 7: 2ª RFEF

1. Investigar fuentes (BeSoccer + posible Transfermarkt)
2. Probar con 1 equipo
3. Evaluar valor de mercado disponible
4. Crear script específico
5. Extracción masiva (4 grupos × 3 temporadas)
6. Cargar a BD

---

### 🔮 Sprint 8: 1ª RFEF

1. Investigar fuentes (BeSoccer + Transfermarkt confirmado)
2. Integrar valor de mercado desde Transfermarkt
3. Probar con 1 equipo
4. Crear script específico
5. Extracción masiva
6. Cargar a BD

---

### 🔮 Sprint 9: 2ª División

1. Investigar fuentes (BeSoccer + Transfermarkt + FBRef)
2. Integrar métricas avanzadas (xG, xA, etc.)
3. Probar con 1 equipo
4. Crear script específico
5. Extracción masiva
6. Cargar a BD

---

### 🔮 Sprint 10+: Expansión

- Más temporadas históricas
- Dashboard de visualización
- API de consulta
- Actualizaciones automáticas durante temporada
- Integración con más fuentes (Wyscout, InStat)

---

## 📂 ESTRUCTURA DE PROYECTO

```
iberscout/
│
├── doc/
│   ├── ESTRATEGIA_PROYECTO.md              ← Este documento
│   ├── GUIA_INTERPRETACION_DATOS.md        ← Documentación de BD (actualizar en cada sprint)
│   ├── INSTRUCCIONES_SPRINT4.md            ← Instrucciones de sprints anteriores
│   └── ...
│
├── research/
│   ├── scrapers_test/
│   │   ├── 02_analisis_liga.py             ← Script original (4 equipos)
│   │   ├── 03_load_to_db.py                ← Carga CSV → PostgreSQL
│   │   ├── 04_fuzzy_matching_test.py       ← POC fuzzy matching
│   │   ├── 05_fuzzy_matching_bd.py         ← Fuzzy matching en BD
│   │   ├── extraer_equipos_liga.py         ← Extracción automática de equipos (1 grupo)
│   │   ├── 06_extraccion_liga_completa.py  ← Scraping masivo (1 temporada, 1 grupo)
│   │   │
│   │   ├── 07_extraccion_3rfef_completa.py      ← [SPRINT 5] Multi-grupo, multi-temporada
│   │   ├── 08_exploracion_lapreferente.py       ← [SPRINT 5] Probar LaPreferente
│   │   ├── 09_exploracion_futbolme.py           ← [SPRINT 5] Probar FutbolMe
│   │   ├── reset_database.py                    ← [SPRINT 5] Limpiar BD
│   │   │
│   │   ├── 10_extraccion_division_honor.py      ← [SPRINT 6] División Honor Juvenil
│   │   ├── 11_extraccion_2rfef.py               ← [SPRINT 7] 2ª RFEF
│   │   └── ...
│   │
│   ├── data_samples/
│   │   └── analisis_ligas/
│   │       ├── equipos_3rfef_grupo1.json
│   │       ├── liga_completa_20251120_123932.csv
│   │       └── ...
│   │
│   └── sql/
│       ├── 01_create_players_temp.sql      ← Schema actual (temporal)
│       └── 02_create_players_final.sql     ← [SPRINT 5] Schema definitivo
│
└── ...
```

---

## ⚠️ PRINCIPIOS IMPORTANTES

### 1. **NO duplicar datos sin control**
- Cada extracción masiva definitiva debe hacerse con BD vacía (TRUNCATE)
- Solo usar fuzzy matching si hay cargas incrementales/experimentales
- Una extracción única = cero duplicados

### 2. **Validar SIEMPRE con 1 equipo primero**
- No lanzar scraping de 360 equipos sin probar antes
- Verificar estructura HTML no ha cambiado
- Confirmar calidad de datos

### 3. **Documentar TODO en `/doc`**
- Cada sprint debe actualizar documentación
- `GUIA_INTERPRETACION_DATOS.md` es la fuente de verdad
- Incluir queries de ejemplo para cada nueva métrica

### 4. **Scripts específicos por liga**
- NO intentar un script "universal" para todas las ligas
- Cada liga tiene su complejidad
- Mejor mantenibilidad con scripts separados

### 5. **Web scraping ético**
- Delays entre peticiones (3-7 segundos)
- User-Agent realista
- Reintentos con backoff exponencial
- No sobrecargar servidores

### 6. **Commits frecuentes**
- Commit después de cada tarea completada
- Push al branch de desarrollo
- Mensajes descriptivos con contexto

---

## 🎯 PRÓXIMO PASO INMEDIATO

### AHORA MISMO (Sprint 5 - Fase 1):

1. **Explorar BeSoccer en detalle**
   - Investigar si fichas individuales tienen más datos
   - Probar con 1 jugador específico
   - Documentar hallazgos

2. **Probar LaPreferente**
   - Crear `08_exploracion_lapreferente.py`
   - Extraer 1 equipo de prueba
   - Comparar con BeSoccer

3. **Decidir estrategia de datos**
   - ¿BeSoccer solo?
   - ¿Combinar múltiples fuentes?
   - Actualizar esquema BD según decisión

---

## 📞 CONTACTO Y FEEDBACK

Este documento es un **trabajo vivo**. Debe actualizarse en cada sprint con:
- Nuevos hallazgos sobre fuentes de datos
- Cambios en el esquema de BD
- Lecciones aprendidas
- Ajustes de estrategia

**Última actualización:** 20 Noviembre 2025 - Sprint 5 iniciado
