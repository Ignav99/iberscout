# 📖 GUÍA DE INTERPRETACIÓN DE DATOS - IBERSCOUT

## 🎯 Sprint 2 Completado

✅ **110 jugadores cargados** en PostgreSQL
✅ **Base de datos operativa** en `research.players_temp`
✅ **Datos listos** para análisis y fuzzy matching

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

## 📝 QUERIES SQL CORRECTAS

### ✅ Top 10 Goleadores (sin porteros)

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

### ✅ Porteros menos goleados

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

### ✅ Jugadores por posición con estadísticas

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

### ✅ Jugadores más activos (partidos jugados)

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

## 📞 PRÓXIMOS PASOS

✅ Sprint 2 completado
🔜 **Sprint 3**: Fuzzy Matching (identificar jugadores duplicados)
🔜 **Sprint 4**: Extracción masiva (liga completa)
🔜 **Sprint 5**: Análisis exploratorio con Jupyter

---

**Última actualización**: Sprint 2 - Noviembre 2025
**Autor**: Proyecto IberScout
