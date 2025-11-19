# 🔧 CHEAT SHEET - IBERSCOUT

## Comandos esenciales que usarás a diario

---

## 🐍 Python y Entorno Virtual

```bash
# Activar entorno virtual (⚠️ HACER SIEMPRE PRIMERO)
source .venv/bin/activate

# Verificar que está activo (debe mostrar (.venv) al inicio)
which python

# Desactivar entorno virtual
deactivate

# Instalar nueva dependencia
pip install nombre_libreria

# Ver todas las librerías instaladas
pip list

# Actualizar una librería
pip install --upgrade nombre_libreria

# Congelar dependencias actuales
pip freeze > requirements/research.txt
```

---

## 🐳 Docker y PostgreSQL

```bash
# Levantar todos los contenedores
docker-compose up -d

# Ver contenedores corriendo
docker ps

# Ver logs de PostgreSQL
docker-compose logs -f postgres

# Parar contenedores
docker-compose down

# Parar contenedores Y BORRAR DATOS (⚠️ CUIDADO)
docker-compose down -v

# Reiniciar solo PostgreSQL
docker-compose restart postgres

# Entrar al contenedor de PostgreSQL
docker exec -it iberscout_postgres bash

# Conectar directamente a psql
docker exec -it iberscout_postgres psql -U iberscout_user -d iberscout_db
```

---

## 🗄️ PostgreSQL (dentro de psql)

```sql
-- Listar todas las bases de datos
\l

-- Conectar a iberscout_db
\c iberscout_db

-- Listar schemas
\dn

-- Listar todas las tablas
\dt

-- Listar tablas del schema research
\dt research.*

-- Describir una tabla
\d research.players_temp

-- Ver datos de una tabla
SELECT * FROM research.players_temp LIMIT 10;

-- Contar registros
SELECT COUNT(*) FROM research.players_temp;

-- Salir de psql
\q
```

---

## 📊 Consultas SQL Útiles

```sql
-- Ver últimos registros scrapeados
SELECT * FROM research.raw_scraping_data 
ORDER BY scraped_at DESC 
LIMIT 10;

-- Contar jugadores por equipo
SELECT team, COUNT(*) as total_players
FROM research.players_temp
GROUP BY team
ORDER BY total_players DESC;

-- Buscar jugador por nombre (fuzzy)
SELECT * FROM research.players_temp
WHERE full_name ILIKE '%messi%';

-- Edad promedio por posición
SELECT position, AVG(age) as avg_age
FROM research.players_temp
WHERE age IS NOT NULL
GROUP BY position
ORDER BY avg_age;
```

---

## 🕷️ Scrapers

```bash
# Ejecutar scraper de prueba (BeSoccer)
python research/scrapers_test/01_test_scraper.py

# Ejecutar en modo headless (sin ver el navegador)
# Editar el script y cambiar: headless=True

# Ver datos scrapeados
ls -lh research/data_samples/

# Ver contenido de un JSON scrapeado
cat research/data_samples/besoccer_test_*.json | python -m json.tool
```

---

## 📁 Gestión de Archivos

```bash
# Ver estructura del proyecto
tree -L 2 -I '.venv|__pycache__|*.pyc'

# Buscar archivos CSV recientes
find data/ -name "*.csv" -type f -mtime -1

# Comprimir carpeta de datos
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/

# Limpiar datos temporales (⚠️ CUIDADO)
rm -rf research/data_samples/*
rm -rf data/raw/*
```

---

## 🐛 Debugging y Logs

```bash
# Ver últimas 50 líneas del log
tail -n 50 logs/iberscout.log

# Seguir el log en tiempo real
tail -f logs/iberscout.log

# Buscar errores en el log
grep "ERROR" logs/iberscout.log

# Ver solo warnings y errores
grep -E "WARNING|ERROR" logs/iberscout.log

# Limpiar logs antiguos
> logs/iberscout.log  # Vacía el archivo
```

---

## 🧪 Testing y Validación

```bash
# Verificar configuración completa
python verificar_entorno.py

# Test de conexión a base de datos
python research/test_db_connection.py

# Ejecutar Jupyter Notebook
jupyter notebook

# Abrir IPython (Python interactivo)
ipython
```

---

## 📦 Pandas (en Python/IPython)

```python
import pandas as pd

# Leer CSV
df = pd.read_csv('data/raw/players.csv')

# Ver primeras filas
df.head()

# Info general
df.info()

# Estadísticas descriptivas
df.describe()

# Filtrar
df[df['age'] > 25]

# Agrupar
df.groupby('position')['age'].mean()

# Guardar procesado
df.to_csv('data/processed/players_clean.csv', index=False)
```

---

## 🔍 Búsqueda y Navegación

```bash
# Buscar en archivos Python
grep -r "def scrape" research/

# Buscar texto en todos los scripts
grep -r "BeSoccer" --include="*.py"

# Contar líneas de código Python
find . -name "*.py" -not -path "./.venv/*" | xargs wc -l

# Ver archivos modificados hoy
find . -type f -mtime 0

# Abrir proyecto en VS Code
code .
```

---

## 🌐 Playwright

```bash
# Instalar/actualizar navegadores
playwright install

# Instalar solo Chromium
playwright install chromium

# Ver navegadores instalados
playwright install --help

# Generar código de scraping automáticamente (codegen)
playwright codegen https://www.besoccer.com
```

---

## 🔄 Git (cuando inicialices el repo)

```bash
# Inicializar repositorio
git init

# Ver estado
git status

# Añadir todos los archivos
git add .

# Commit
git commit -m "Mensaje descriptivo"

# Ver historial
git log --oneline

# Ver diferencias
git diff

# Crear rama nueva
git checkout -b feature/nueva-funcionalidad

# Volver a main
git checkout main
```

---

## 🛠️ Mantenimiento

```bash
# Ver espacio usado por directorios
du -sh data/*/

# Limpiar archivos Python compilados
find . -type d -name "__pycache__" -exec rm -r {} +

# Actualizar pip
pip install --upgrade pip

# Recrear entorno virtual (si está corrupto)
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/research.txt
```

---

## 🚨 Comandos de Emergencia

```bash
# Parar todo Docker
docker stop $(docker ps -aq)

# Reiniciar Docker
killall Docker && open /Applications/Docker.app

# Liberar puerto 5432 (si está ocupado)
lsof -ti:5432 | xargs kill -9

# Forzar cierre de Python
pkill -9 python

# Ver procesos de Python corriendo
ps aux | grep python
```

---

## 💡 Tips y Trucos

### Alias útiles (añadir a ~/.zshrc o ~/.bashrc)

```bash
# Activar entorno de iberscout
alias iber="cd ~/Documents/iberscout && source .venv/bin/activate"

# Ver logs de iberscout
alias iberlogs="tail -f ~/Documents/iberscout/logs/iberscout.log"

# Levantar Docker de iberscout
alias iberup="cd ~/Documents/iberscout && docker-compose up -d"

# Parar Docker de iberscout
alias iberdown="cd ~/Documents/iberscout && docker-compose down"

# Después de añadirlos:
source ~/.zshrc  # O source ~/.bashrc
```

### Atajos de teclado útiles

- **Ctrl + C**: Detener proceso actual
- **Ctrl + D**: Salir de Python/IPython/psql
- **Ctrl + L**: Limpiar terminal
- **Ctrl + R**: Buscar en historial de comandos
- **⌘ + K**: Limpiar terminal (Mac iTerm2)

---

## 📋 Checklist Diario

Al empezar a trabajar:

```bash
# 1. Activar entorno
source .venv/bin/activate

# 2. Verificar Docker
docker ps

# 3. Si no está corriendo PostgreSQL
docker-compose up -d

# 4. Pull cambios (si usas Git)
git pull

# 5. Ver estado del proyecto
python verificar_entorno.py
```

Al terminar:

```bash
# 1. Commit si hiciste cambios (Git)
git add .
git commit -m "Descripción de cambios"

# 2. (Opcional) Parar Docker si no lo usarás
docker-compose down

# 3. Desactivar entorno virtual
deactivate
```

---

## 🎓 Recursos Rápidos

### Documentación oficial
- Playwright: `playwright.dev/python`
- Pandas: `pandas.pydata.org/docs`
- PostgreSQL: `postgresql.org/docs`

### Cuando tengas dudas
```bash
# Ver ayuda de un comando
comando --help

# Documentación de librería Python
python -c "import libreria; help(libreria)"

# Ver código fuente de una función
import inspect
print(inspect.getsource(funcion))
```

---

**💡 Tip**: Imprime esta hoja y tenla cerca de tu escritorio. La usarás constantemente. 🚀

**Última actualización**: 19-Nov-2025
