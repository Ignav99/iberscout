# 📋 INSTRUCCIONES SPRINT 2 - Carga en PostgreSQL

## 🎯 Objetivo
Cargar los datos extraídos por el scraper en la base de datos PostgreSQL.

---

## ✅ PRE-REQUISITOS

Antes de empezar, verifica:

1. **Docker está corriendo**:
   ```bash
   docker-compose ps
   ```
   Debe mostrar `iberscout_postgres` con estado `Up`

2. **Si Docker NO está corriendo**, levántalo:
   ```bash
   docker-compose up -d
   ```

3. **Tienes el CSV generado** por `02_analisis_liga.py`
   - Debe estar en: `research/data_samples/analisis_ligas/jugadores_final_*.csv`
   - Si NO existe, ejecuta primero: `python research/scrapers_test/02_analisis_liga.py`

---

## 📝 PASOS A SEGUIR

### **PASO 1: Hacer pull de los cambios**

```bash
git pull origin claude/review-project-docs-0156d9ResrsQQyvq3SB1TFkN
```

---

### **PASO 2: Crear la tabla en PostgreSQL**

Ejecuta el script SQL que crea la tabla `research.players_temp`:

```bash
psql -h localhost -p 5433 -U iberscout_user -d iberscout_db -f research/scrapers_test/sql/01_create_players_temp.sql
```

**Contraseña cuando la pida**: `TIZ@voltio999`

**Salida esperada**:
```
✅ Debe mostrar la estructura de la tabla
✅ Debe decir "total_jugadores | 0" (porque aún no hay datos)
```

---

### **PASO 3: Cargar los datos del CSV a PostgreSQL**

```bash
python research/scrapers_test/03_load_to_db.py
```

**Salida esperada**:
```
📥 CARGA DE DATOS CSV → POSTGRESQL (SPRINT 2)
1️⃣  Buscando archivo CSV...
   ✅ Encontrado: jugadores_final_XXXXXX.csv
2️⃣  Leyendo CSV...
   ✅ CSV leído: 108 registros, 9 columnas
3️⃣  Conectando a PostgreSQL...
   ✅ Conectado a PostgreSQL: iberscout_db
4️⃣  Verificando tabla research.players_temp...
   ✅ Tabla existe
5️⃣  Limpiando datos...
   ✅ Datos limpios: 108 registros válidos
6️⃣  Cargando 108 registros en PostgreSQL...
   ✅ 108 registros insertados exitosamente
7️⃣  VERIFICACIÓN DE DATOS CARGADOS
   ✅ Total de jugadores en BD: 108
   ...estadísticas...
🎉 CARGA COMPLETADA EXITOSAMENTE
```

---

### **PASO 4: Verificar los datos (OPCIONAL)**

Si quieres explorar la base de datos manualmente:

```bash
psql -h localhost -p 5433 -U iberscout_user -d iberscout_db
```

Dentro de `psql`, puedes ejecutar:

```sql
-- Ver todos los jugadores
SELECT * FROM research.players_temp LIMIT 10;

-- Contar por equipo
SELECT equipo, COUNT(*) FROM research.players_temp GROUP BY equipo;

-- Top goleadores
SELECT nombre, equipo, goles FROM research.players_temp ORDER BY goles DESC LIMIT 5;

-- Salir
\q
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "No module named 'psycopg2'"

**Solución**:
```bash
pip install psycopg2-binary pandas
```

---

### ❌ Error: "connection refused"

**Solución**:
1. Verifica que Docker esté corriendo:
   ```bash
   docker-compose ps
   ```

2. Si NO está corriendo, levántalo:
   ```bash
   docker-compose up -d
   ```

3. Espera 10 segundos y prueba de nuevo

---

### ❌ Error: "No se encontraron archivos CSV"

**Solución**:
Ejecuta primero el scraper para generar el CSV:
```bash
python research/scrapers_test/02_analisis_liga.py
```

---

### ❌ Error: "La tabla research.players_temp NO existe"

**Solución**:
Ejecuta primero el PASO 2 (crear la tabla con el script SQL)

---

## 📤 RESULTADO FINAL

Una vez completados todos los pasos:

1. **Copia TODA la salida del PASO 3** (script Python)
2. **Pégala en el chat** para que podamos analizar juntos
3. **Si hubo errores**, copia también el mensaje de error completo

---

## 🎯 Siguiente Sprint

Una vez que verifiquemos que los datos están correctamente cargados, continuaremos con:

**SPRINT 3: Fuzzy Matching** - Identificar jugadores duplicados con nombres similares

---

**Última actualización**: Sprint 2 - Noviembre 2025
