# 📊 GUÍA DE INTERPRETACIÓN DE DATOS - IBERSCOUT v1.0

**Última actualización:** 20 Noviembre 2025
**Versión de BD:** v1.0 - 3ª RFEF Completa
**Fuente primaria:** BeSoccer (plantillas + fichas individuales)

---

## 📋 ESTRUCTURA DE LA BASE DE DATOS

### Tabla: `research.players`

Base de datos definitiva v1 con datos extendidos de 3ª RFEF.

---

## 🔢 CAMPOS DE LA TABLA

### **CAMPOS CORE** (Identificación)

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | SERIAL | NO | ID único autogenerado |
| `nombre` | VARCHAR(200) | NO | Nombre del jugador (tal como aparece en BeSoccer) |
| `dorsal` | INTEGER | SÍ | Número de dorsal (0-99) |
| `posicion` | VARCHAR(50) | SÍ | Portero, Defensa, Centrocampista, Delantero |
| `edad` | INTEGER | SÍ | Edad al momento de extracción (15-50) |
| `equipo` | VARCHAR(200) | NO | Nombre del equipo |
| `liga` | VARCHAR(100) | NO | "3ª RFEF - [Grupo]" |
| `temporada` | VARCHAR(10) | NO | "2024/25", "2023/24", "2022/23" |

---

### **ESTADÍSTICAS BÁSICAS** (Tabla de plantilla)

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `partidos_jugados` | INTEGER | SÍ | Total partidos jugados (titular + suplente) |
| `partidos_titular` | INTEGER | SÍ | Partidos jugados como titular |
| `goles` | INTEGER | SÍ | Goles marcados (⚠️ para porteros = goles encajados) |
| `asistencias` | INTEGER | SÍ | Asistencias realizadas |

---

### **ESTADÍSTICAS EXTENDIDAS** (Ficha individual) ⭐ NUEVO

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `minutos_jugados` | INTEGER | SÍ | Minutos totales jugados en la temporada |
| `pie_dominante` | VARCHAR(20) | SÍ | "Derecho", "Izquierdo", "Ambidiestro" |
| `nacionalidad` | VARCHAR(50) | SÍ | Nacionalidad (mayormente NULL en 3ª RFEF) |

---

### **METADATA**

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `source` | VARCHAR(50) | SÍ | Fuente de datos (default: "besoccer") |
| `scraped_at` | TIMESTAMP | SÍ | Fecha/hora de extracción |

---

## ⚠️ INTERPRETACIONES ESPECIALES

### 1. **Campo `goles` para PORTEROS**

**Interpretación diferente según posición:**

```sql
-- Goles MARCADOS (jugadores de campo)
SELECT nombre, goles
FROM research.players
WHERE posicion IN ('Defensa', 'Centrocampista', 'Delantero')
  AND goles > 0
ORDER BY goles DESC;

-- Goles ENCAJADOS (porteros)
SELECT nombre, goles as goles_encajados
FROM research.players
WHERE posicion = 'Portero'
ORDER BY goles ASC;  -- Menos goles encajados = mejor
```

**Explicación:** BeSoccer no tiene columnas separadas. Para porteros, el valor en `goles` representa los goles que han encajado.

---

### 2. **Campo `minutos_jugados`**

Puede ser NULL en dos casos:
1. **Jugador sin debut**: 0 partidos jugados
2. **No disponible en ficha**: BeSoccer no tiene el dato para esa temporada
3. **Optimización de extracción**: Solo se extraen minutos para jugadores con ≥3 partidos

```sql
-- Jugadores con minutos registrados
SELECT nombre, partidos_jugados, minutos_jugados,
       (minutos_jugados::float / NULLIF(partidos_jugados, 0)) as minutos_por_partido
FROM research.players
WHERE minutos_jugados IS NOT NULL
  AND partidos_jugados > 0
ORDER BY minutos_jugados DESC;
```

---

### 3. **Campo `temporada`**

Formato: `YYYY/YY`

Ejemplos:
- `2024/25` → Temporada 2024-2025
- `2023/24` → Temporada 2023-2024
- `2022/23` → Temporada 2022-2023

```sql
-- Jugadores por temporada
SELECT temporada, COUNT(*) as jugadores
FROM research.players
GROUP BY temporada
ORDER BY temporada DESC;
```

---

### 4. **Campo `liga`**

Formato: `"3ª RFEF - [Nombre del Grupo]"`

Ejemplos:
- `"3ª RFEF - Galicia"`
- `"3ª RFEF - Madrid"`
- `"3ª RFEF - Andalucía Oriental"`

```sql
-- Extraer solo el grupo
SELECT SUBSTRING(liga FROM 'RFEF - (.+)') as grupo,
       COUNT(*) as jugadores
FROM research.players
GROUP BY grupo
ORDER BY jugadores DESC;
```

---

## 📊 CONSULTAS SQL ÚTILES

### **Scouting: Mejores goleadores**

```sql
SELECT nombre, equipo, posicion, goles, partidos_jugados,
       ROUND(goles::numeric / NULLIF(partidos_jugados, 0), 2) as goles_por_partido
FROM research.players
WHERE temporada = '2024/25'
  AND posicion != 'Portero'
  AND partidos_jugados >= 5
ORDER BY goles DESC
LIMIT 20;
```

---

### **Scouting: Jugadores con más minutos**

```sql
SELECT nombre, equipo, edad, posicion,
       minutos_jugados, partidos_jugados,
       ROUND(minutos_jugados::numeric / NULLIF(partidos_jugados, 0), 0) as minutos_por_partido
FROM research.players
WHERE temporada = '2024/25'
  AND minutos_jugados IS NOT NULL
  AND minutos_jugados >= 500
ORDER BY minutos_jugados DESC
LIMIT 20;
```

---

### **Scouting: Mejores porteros (menos goles encajados)**

```sql
SELECT nombre, equipo, edad,
       partidos_jugados, goles as goles_encajados,
       ROUND(goles::numeric / NULLIF(partidos_jugados, 0), 2) as goles_por_partido
FROM research.players
WHERE temporada = '2024/25'
  AND posicion = 'Portero'
  AND partidos_jugados >= 5
ORDER BY goles_por_partido ASC  -- Menos = mejor
LIMIT 20;
```

---

### **Análisis: Distribución de edades por posición**

```sql
SELECT posicion,
       COUNT(*) as jugadores,
       ROUND(AVG(edad), 1) as edad_promedio,
       MIN(edad) as edad_min,
       MAX(edad) as edad_max
FROM research.players
WHERE temporada = '2024/25'
  AND edad IS NOT NULL
GROUP BY posicion
ORDER BY posicion;
```

---

### **Análisis: Jugadores zurdos vs diestros**

```sql
SELECT pie_dominante,
       COUNT(*) as jugadores,
       ROUND(COUNT(*)::numeric * 100 / SUM(COUNT(*)) OVER (), 1) as porcentaje
FROM research.players
WHERE temporada = '2024/25'
  AND pie_dominante IS NOT NULL
GROUP BY pie_dominante
ORDER BY jugadores DESC;
```

---

### **Análisis: Equipos con más goles**

```sql
SELECT equipo,
       SUM(goles) FILTER (WHERE posicion != 'Portero') as goles_totales,
       COUNT(*) as jugadores,
       ROUND(AVG(goles) FILTER (WHERE posicion != 'Portero'), 2) as goles_por_jugador
FROM research.players
WHERE temporada = '2024/25'
GROUP BY equipo
ORDER BY goles_totales DESC
LIMIT 20;
```

---

### **Comparativa multi-temporada de un jugador**

```sql
SELECT temporada, equipo, edad,
       partidos_jugados, partidos_titular, goles, asistencias,
       minutos_jugados
FROM research.players
WHERE nombre = 'Canedo'
ORDER BY temporada DESC;
```

---

### **Scouting: Jóvenes promesas (sub-21 destacados)**

```sql
SELECT nombre, equipo, edad, posicion,
       partidos_jugados, goles, asistencias, minutos_jugados
FROM research.players
WHERE temporada = '2024/25'
  AND edad <= 21
  AND partidos_jugados >= 10
ORDER BY goles DESC, asistencias DESC
LIMIT 30;
```

---

### **Análisis: Regularidad de jugadores (titular vs suplente)**

```sql
SELECT nombre, equipo, posicion,
       partidos_jugados, partidos_titular,
       ROUND(partidos_titular::numeric / NULLIF(partidos_jugados, 0) * 100, 1) as porcentaje_titular
FROM research.players
WHERE temporada = '2024/25'
  AND partidos_jugados >= 10
ORDER BY porcentaje_titular DESC
LIMIT 20;
```

---

## 📈 DISPONIBILIDAD DE DATOS POR CAMPO

| Campo | 3ª RFEF 2024/25 | 3ª RFEF 2023/24 | 3ª RFEF 2022/23 | Notas |
|-------|-----------------|-----------------|-----------------|-------|
| nombre | ✅ 100% | ✅ 100% | ✅ 100% | Siempre disponible |
| dorsal | ✅ ~98% | ✅ ~98% | ✅ ~98% | Ocasionalmente NULL |
| posicion | ✅ 100% | ✅ 100% | ✅ 100% | Siempre disponible |
| edad | ✅ ~95% | ✅ ~95% | ✅ ~95% | Algunos NULL |
| partidos_jugados | ✅ 100% | ✅ 100% | ✅ 100% | Default 0 |
| goles | ✅ 100% | ✅ 100% | ✅ 100% | Default 0 |
| asistencias | ✅ 100% | ✅ 100% | ✅ 100% | Default 0 |
| **minutos_jugados** | ⚠️ ~70% | ⚠️ ~70% | ⚠️ ~70% | Solo jugadores con ≥3 partidos |
| **pie_dominante** | ⚠️ ~60% | ⚠️ ~60% | ⚠️ ~60% | Disponible en fichas |
| **nacionalidad** | ⚠️ ~10% | ⚠️ ~10% | ⚠️ ~10% | Mayormente NULL en 3ª RFEF |

---

## 🚫 DATOS NO DISPONIBLES (v1.0)

Los siguientes datos **NO están** disponibles en esta versión:

| Campo | Estado | Motivo |
|-------|--------|--------|
| Tarjetas amarillas | ❌ NO | BeSoccer no las tiene para 3ª RFEF |
| Tarjetas rojas | ❌ NO | BeSoccer no las tiene para 3ª RFEF |
| Altura | ❌ NO | BeSoccer no tiene datos físicos en 3ª RFEF |
| Peso | ❌ NO | BeSoccer no tiene datos físicos en 3ª RFEF |
| Valor de mercado | ❌ NO | No aplica para 3ª RFEF |
| xG / xA | ❌ NO | No disponible en categorías inferiores |

**Futuro:** Sprint 6+ evaluaremos agregar tarjetas desde otras fuentes (LaPreferente).

---

## 🔄 ACTUALIZACIONES Y VERSIONES

### **v1.0 - 20 Noviembre 2025** (ACTUAL)
- ✅ Tabla `research.players` definitiva
- ✅ Datos de 3ª RFEF (18 grupos)
- ✅ 3 temporadas: 2024/25, 2023/24, 2022/23
- ✅ Campos extendidos: minutos, pie dominante, nacionalidad
- ✅ Fuente: BeSoccer (plantillas + fichas individuales)

### **Próximas versiones:**
- **v1.1**: Agregar 2ª RFEF (4 grupos)
- **v1.2**: Agregar 1ª RFEF (2 grupos)
- **v2.0**: Integrar tarjetas amarillas/rojas desde LaPreferente
- **v2.1**: Agregar División de Honor Juvenil

---

## 📞 CONTACTO Y FEEDBACK

Para sugerencias, errores o mejoras de esta documentación:
- Actualizar este archivo directamente
- Incluir fecha de cambio
- Documentar razón del cambio

**Última revisión:** 20 Noviembre 2025 - Sprint 5
