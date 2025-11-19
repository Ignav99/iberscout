# 📋 PLAN DE TRABAJO - FASE DE INVESTIGACIÓN

## 🎯 Objetivo de esta fase
Validar que podemos extraer datos de las fuentes principales sin problemas técnicos antes de construir el sistema completo.

---

## 🏗️ SPRINT 0: Setup y Validación (ACTUAL)

### ✅ Tareas completadas
- [x] Estructura de carpetas creada
- [x] Docker Compose configurado
- [x] PostgreSQL levantado
- [x] Conexión a base de datos verificada
- [x] Entorno virtual Python configurado

### 📝 Próximas tareas
- [ ] Ejecutar script de prueba `01_test_scraper.py`
- [ ] Verificar que no hay bloqueos en BeSoccer
- [ ] Documentar capturas de pantalla

---

## 🕷️ SPRINT 1: Extracción Piloto - UN Equipo

**Duración estimada**: 2-3 días  
**Objetivo**: Extraer datos completos de UN solo equipo de 3ª RFEF

### Fuente elegida: BeSoccer (más amigable)

#### Tareas
1. **Identificar equipo objetivo**
   - Elegir: CD Ebro, Atlético Monzón, o similar
   - Anotar URL exacta del equipo

2. **Desarrollar scraper específico**
   ```
   research/scrapers_test/02_besoccer_equipo.py
   ```
   - Extraer lista de jugadores
   - Datos: Nombre, Posición, Edad, Nacionalidad
   - Guardar en CSV temporal

3. **Validación manual**
   - Comparar CSV con página web
   - Verificar acentos, caracteres especiales
   - Comprobar que no faltan jugadores

4. **Iterar si es necesario**
   - Ajustar selectores CSS/XPath
   - Manejar excepciones (jugadores sin edad, etc.)

### 📊 Entregable
- CSV con ~25 jugadores del equipo elegido
- Script funcional y documentado
- Notas sobre dificultades encontradas

---

## 🗄️ SPRINT 2: Primera Carga en Base de Datos

**Duración estimada**: 2 días  
**Objetivo**: Llevar los datos del CSV a PostgreSQL

### Tareas
1. **Diseñar tabla temporal**
   ```sql
   CREATE TABLE research.players_temp (
       id SERIAL PRIMARY KEY,
       full_name VARCHAR(200),
       position VARCHAR(50),
       age INTEGER,
       nationality VARCHAR(100),
       team VARCHAR(200),
       source_url TEXT,
       scraped_at TIMESTAMP
   );
   ```

2. **Script de carga**
   ```
   research/scrapers_test/03_load_to_db.py
   ```
   - Leer CSV con Pandas
   - Insertar en PostgreSQL con SQLAlchemy
   - Manejar duplicados

3. **Verificación**
   - Query SQL para contar registros
   - Verificar datos en PgAdmin (opcional)

### 📊 Entregable
- Tabla `research.players_temp` con datos
- Script de carga funcional

---

## 🔍 SPRINT 3: Fuzzy Matching - Prueba de Concepto

**Duración estimada**: 2-3 días  
**Objetivo**: Probar algoritmo de matching de nombres

### Escenario
Tenemos el mismo jugador en dos fuentes con nombres ligeramente diferentes:
- BeSoccer: "J. Bellingham"
- Transfermarkt: "Jude Bellingham"

### Tareas
1. **Crear dataset de prueba**
   - Manual: 20 nombres con variaciones
   - Ejemplo: "Leo Messi" / "Lionel Messi" / "L. Messi"

2. **Implementar algoritmo**
   ```
   research/scrapers_test/04_fuzzy_matching.py
   ```
   - Usar librería `thefuzz`
   - Calcular similitud de cadenas
   - Definir umbral (ej. 85% = match probable)

3. **Evaluar resultados**
   - True Positives: Matches correctos
   - False Positives: Matches incorrectos
   - Ajustar umbral si es necesario

### 📊 Entregable
- Jupyter Notebook con resultados
- Documentación de casos edge (nombres complicados)

---

## 🚀 SPRINT 4: Extracción Masiva - Liga Completa

**Duración estimada**: 3-4 días  
**Objetivo**: Extraer TODOS los equipos de una competición pequeña

### Liga elegida: 3ª RFEF Grupo X (el que tenga el Central)

### Tareas
1. **Scraper recursivo**
   ```
   research/scrapers_test/05_liga_completa.py
   ```
   - Iterar por todos los equipos
   - Delay entre equipos (3-7 segundos)
   - Sistema de reintentos si falla

2. **Gestión de errores**
   - Log detallado de errores
   - Continuar ejecución si falla 1 equipo
   - Guardar progreso incremental

3. **Monitoreo**
   - Barra de progreso (tqdm)
   - Tiempo estimado de finalización

### 📊 Entregable
- Base de datos con ~400-500 jugadores
- Log de ejecución sin errores críticos

---

## 📈 SPRINT 5: Análisis Exploratorio

**Duración estimada**: 2 días  
**Objetivo**: Hacer consultas SQL y visualizaciones básicas

### Tareas
1. **Jupyter Notebook**
   ```
   research/notebooks/01_analisis_exploratorio.ipynb
   ```

2. **Consultas a implementar**
   - Distribución por posiciones
   - Edad promedio por equipo
   - Nacionalidades más comunes
   - Equipos con más jugadores extranjeros

3. **Visualizaciones**
   - Gráfico de barras: Jugadores por equipo
   - Histograma: Distribución de edades
   - Mapa de calor: Posiciones más comunes

### 📊 Entregable
- Notebook con insights básicos
- Validar que los datos tienen sentido

---

## 🎓 DECISIÓN: ¿Seguir o Pivotar?

Al finalizar el Sprint 5, revisaremos:

### ✅ Seguir adelante si:
- Los scrapers son robustos (< 5% errores)
- Los datos son de calidad (sin muchos nulos)
- El fuzzy matching funciona (> 90% precisión)
- No hay bloqueos constantes de IPs

### 🔄 Pivotar si:
- Bloqueos frecuentes → Considerar APIs de pago
- Datos de baja calidad → Cambiar fuente principal
- Demasiados errores → Simplificar alcance

---

## 📅 Calendario Tentativo

| Sprint | Duración | Fecha Inicio | Fecha Fin |
|--------|----------|--------------|-----------|
| 0 - Setup | 1 día | 19-Nov | 20-Nov |
| 1 - Piloto | 3 días | 20-Nov | 23-Nov |
| 2 - DB | 2 días | 23-Nov | 25-Nov |
| 3 - Matching | 3 días | 25-Nov | 28-Nov |
| 4 - Masivo | 4 días | 28-Nov | 2-Dic |
| 5 - Análisis | 2 días | 2-Dic | 4-Dic |

**REVISIÓN FINAL**: 4-Dic  
**INICIO FASE PRODUCCIÓN**: 5-Dic (si todo va bien)

---

## 🛠️ Herramientas de Seguimiento

### Daily Checklist
Cada día al empezar:
- [ ] Activar entorno virtual
- [ ] Pull últimos cambios de Git
- [ ] Revisar logs de scrapers
- [ ] Actualizar este documento

### Al terminar cada Sprint:
- [ ] Commit de código
- [ ] Documentar problemas encontrados
- [ ] Actualizar README con estado
- [ ] Screenshot de resultados

---

## 📞 Contacto y Soporte

Si encuentras problemas:
1. Revisa los logs en `logs/iberscout.log`
2. Consulta la documentación de Playwright
3. Pregunta en Discord/Slack del proyecto

---

**Última actualización**: 19-Nov-2025  
**Autor**: Ignacio - Club Atlético Central
