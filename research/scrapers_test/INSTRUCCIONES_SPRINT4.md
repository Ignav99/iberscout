# 📋 INSTRUCCIONES SPRINT 4 - Extracción Masiva

## 🎯 Objetivo
Extraer TODOS los equipos de un grupo de 3ª RFEF (~20 equipos, ~500 jugadores).

---

## 📝 PASOS A SEGUIR

### **PASO 1: Hacer pull de los cambios**

```bash
git pull origin claude/review-project-docs-0156d9ResrsQQyvq3SB1TFkN
```

---

### **PASO 2: Extraer lista de equipos del grupo**

Este script usa Playwright para obtener todos los equipos de 3ª RFEF Grupo 1 (Galicia):

```bash
python research/scrapers_test/extraer_equipos_liga.py
```

**Salida esperada**:
```
🔍 EXTRAYENDO EQUIPOS DE 3ª RFEF - GRUPO 1
🦊 Lanzando Firefox...
📡 Navegando a https://es.besoccer.com/...
✅ Tabla encontrada
✅ Equipos extraídos: 20

📋 EQUIPOS ENCONTRADOS:
    1. SD Compostela
    2. Racing Villalbés
    3. ...
   20. Equipo X

💾 Lista guardada en: research/data_samples/analisis_ligas/equipos_3rfef_grupo1.json
```

**Esto genera**: Un archivo JSON con la lista de ~20 equipos y sus URLs.

---

### **PASO 3: Scraping masivo de toda la liga**

Ahora ejecuta el script principal que scrapea TODOS los equipos:

```bash
python research/scrapers_test/06_extraccion_liga_completa.py
```

**Qué hace**:
- Lee la lista de equipos del JSON generado en PASO 2
- Itera cada equipo con delays de 3-7 segundos (evita bloqueos)
- Muestra barra de progreso en tiempo real
- Reintentos automáticos (máx 3 intentos) si falla
- Guarda CSV + JSON con TODOS los jugadores

**Salida esperada**:
```
SPRINT 4: EXTRACCIÓN MASIVA - LIGA COMPLETA

📊 Equipos a scrapear: 20
⏱️  Tiempo estimado: 100-200 segundos (~3-5 minutos)
🎯 Objetivo: ~500 jugadores

Presiona ENTER para comenzar...

🦊 Lanzando Firefox...
✅ Firefox listo

Scraping: 100%|████████████████| 20/20 [03:45<00:00, 11.3s/equipo]

📊 RESUMEN DE EXTRACCIÓN
✅ Equipos exitosos: 19/20
✅ Total jugadores: 487

📈 ESTADÍSTICAS RÁPIDAS:
   Edad promedio: 24.3 años
   Jugadores por posición:
      Defensa: 152
      Delantero: 135
      Centrocampista: 121
      Portero: 79

💾 Guardando datos...
   📄 CSV: liga_completa_20251120_123456.csv
   📄 JSON: liga_completa_20251120_123456.json

🎉 ¡EXTRACCIÓN COMPLETADA!
```

---

### **PASO 4: Cargar datos a PostgreSQL**

Usa el mismo script del Sprint 2 (auto-detecta el CSV más reciente):

```bash
python research/scrapers_test/03_load_to_db.py
```

**Esto cargará** los ~500 jugadores nuevos a la BD.

---

### **PASO 5: Verificar duplicados**

Corre fuzzy matching para buscar duplicados en los ~600 jugadores totales (110 antiguos + 500 nuevos):

```bash
python research/scrapers_test/05_fuzzy_matching_bd.py
```

---

## ⏱️ TIEMPO ESTIMADO

- **PASO 2** (extraer equipos): ~10 segundos
- **PASO 3** (scraping masivo): ~3-5 minutos
- **PASO 4** (carga a BD): ~10 segundos
- **PASO 5** (fuzzy matching): ~30 segundos

**Total**: ~5-10 minutos

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "No se encontró equipos_3rfef_grupo1.json"

**Solución**: Ejecuta primero el PASO 2 (`extraer_equipos_liga.py`).

---

### ❌ Error: "Equipos que fallaron"

**Solución**: Es normal que 1-2 equipos fallen (timeouts, páginas sin datos). El script continúa con los demás.

Si quieres reintentar solo los que fallaron, anota los nombres y créalos manualmente en el JSON.

---

### ❌ Error: Connection timeout

**Solución**:
1. Verifica tu conexión a internet
2. Aumenta el timeout en el script (línea: `timeout=60000` → `timeout=120000`)
3. Reintenta

---

## 📊 VALIDACIÓN POST-SCRAPING

Después de cargar a BD, ejecuta estas queries para validar:

```sql
-- Total de jugadores por liga
SELECT liga, COUNT(*)
FROM research.players_temp
GROUP BY liga;

-- Equipos con pocos jugadores (posible error)
SELECT equipo, COUNT(*) as jugadores
FROM research.players_temp
WHERE liga = '3ª RFEF'
GROUP BY equipo
HAVING COUNT(*) < 15
ORDER BY jugadores;

-- Distribución de edades (debe ser normal)
SELECT
    CASE
        WHEN edad < 20 THEN '< 20'
        WHEN edad BETWEEN 20 AND 25 THEN '20-25'
        WHEN edad BETWEEN 26 AND 30 THEN '26-30'
        ELSE '> 30'
    END as rango_edad,
    COUNT(*)
FROM research.players_temp
WHERE liga = '3ª RFEF' AND edad IS NOT NULL
GROUP BY rango_edad
ORDER BY rango_edad;
```

---

## 🎉 AL FINALIZAR

Copia y pega:
1. Output completo del PASO 3 (scraping masivo)
2. Resultado de las queries de validación
3. Cualquier error encontrado

Para que podamos analizar juntos los resultados 👍

---

**Última actualización**: Sprint 4 - Noviembre 2025
