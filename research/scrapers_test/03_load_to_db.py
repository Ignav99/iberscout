"""
==========================================
SPRINT 2: Carga de datos CSV a PostgreSQL
==========================================
Lee el CSV generado por 02_analisis_liga.py y carga los datos en PostgreSQL
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_batch

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,  # Puerto mapeado en docker-compose.yml
    'database': 'iberscout_db',
    'user': 'iberscout_user',
    'password': 'TIZ@voltio999'
}

# Rutas
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "research" / "data_samples" / "analisis_ligas"


def encontrar_csv_mas_reciente():
    """Encuentra el CSV más reciente generado por 02_analisis_liga.py"""
    archivos_csv = list(DATA_DIR.glob("jugadores_final_*.csv"))

    if not archivos_csv:
        print(f"❌ No se encontraron archivos CSV en {DATA_DIR}")
        print(f"\n💡 INSTRUCCIÓN:")
        print(f"   1. Ejecuta primero: python research/scrapers_test/02_analisis_liga.py")
        print(f"   2. Luego ejecuta este script nuevamente")
        return None

    # Ordenar por fecha de modificación (más reciente primero)
    archivo_mas_reciente = sorted(archivos_csv, key=lambda x: x.stat().st_mtime, reverse=True)[0]
    return archivo_mas_reciente


def conectar_db():
    """Conecta a PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"✅ Conectado a PostgreSQL: {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"❌ Error al conectar a PostgreSQL: {e}")
        print(f"\n💡 VERIFICA:")
        print(f"   1. Docker está corriendo: docker-compose ps")
        print(f"   2. PostgreSQL está levantado: docker-compose up -d")
        return None


def verificar_tabla_existe(conn):
    """Verifica si la tabla research.players_temp existe"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'research'
                AND table_name = 'players_temp'
            );
        """)
        existe = cur.fetchone()[0]

    if not existe:
        print(f"❌ La tabla research.players_temp NO existe")
        print(f"\n💡 INSTRUCCIÓN:")
        print(f"   1. Ejecuta el script SQL primero:")
        print(f"      psql -h localhost -p 5433 -U iberscout_user -d iberscout_db -f research/scrapers_test/sql/01_create_players_temp.sql")
        print(f"   2. Contraseña: TIZ@voltio999")
        return False

    return True


def limpiar_datos(df):
    """Limpia y valida los datos antes de insertar"""
    print(f"\n🧹 Limpiando datos...")

    # Reemplazar NaN con None (NULL en SQL)
    df = df.where(pd.notna(df), None)

    # Validaciones
    registros_originales = len(df)

    # Filtrar edades inválidas (fuera de rango 15-50)
    if 'edad' in df.columns:
        invalidos_edad = df[df['edad'].notna() & ((df['edad'] < 15) | (df['edad'] > 50))]
        if len(invalidos_edad) > 0:
            print(f"   ⚠️  {len(invalidos_edad)} jugadores con edad inválida (se mantendrán como NULL)")
            df.loc[invalidos_edad.index, 'edad'] = None

    # Validar que no haya valores negativos en estadísticas
    cols_stats = ['partidos_jugados', 'partidos_titular', 'goles', 'asistencias']
    for col in cols_stats:
        if col in df.columns:
            negativos = df[df[col] < 0]
            if len(negativos) > 0:
                print(f"   ⚠️  {len(negativos)} registros con {col} negativo (se convertirán a 0)")
                df.loc[df[col] < 0, col] = 0

    print(f"   ✅ Datos limpios: {len(df)} registros válidos de {registros_originales} originales")

    return df


def cargar_datos(conn, df):
    """Carga los datos en PostgreSQL usando batch insert"""
    print(f"\n💾 Cargando {len(df)} registros en PostgreSQL...")

    # Preparar datos para inserción
    columnas = ['dorsal', 'nombre', 'posicion', 'partidos_jugados', 'partidos_titular',
                'goles', 'asistencias', 'edad', 'equipo', 'liga']

    # SQL para inserción
    insert_sql = """
        INSERT INTO research.players_temp
        (dorsal, nombre, posicion, partidos_jugados, partidos_titular,
         goles, asistencias, edad, equipo, liga, source, scraped_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Convertir DataFrame a lista de tuplas
    timestamp = datetime.now()
    datos = []
    for _, row in df.iterrows():
        tupla = tuple(row[col] if col in row.index else None for col in columnas)
        tupla = tupla + ('besoccer', timestamp)  # Agregar source y timestamp
        datos.append(tupla)

    # Insertar en batch
    try:
        with conn.cursor() as cur:
            execute_batch(cur, insert_sql, datos, page_size=100)
            conn.commit()
            print(f"   ✅ {len(datos)} registros insertados exitosamente")
        return True
    except Exception as e:
        print(f"   ❌ Error al insertar datos: {e}")
        conn.rollback()
        return False


def verificar_carga(conn):
    """Verifica los datos cargados con queries SQL"""
    print(f"\n📊 VERIFICACIÓN DE DATOS CARGADOS")
    print("=" * 70)

    with conn.cursor() as cur:
        # Total de registros
        cur.execute("SELECT COUNT(*) FROM research.players_temp;")
        total = cur.fetchone()[0]
        print(f"\n✅ Total de jugadores en BD: {total}")

        # Por equipo
        cur.execute("""
            SELECT equipo, liga, COUNT(*) as jugadores
            FROM research.players_temp
            GROUP BY equipo, liga
            ORDER BY liga, equipo;
        """)
        print(f"\n📋 Jugadores por equipo:")
        for row in cur.fetchall():
            print(f"   • {row[0]:25s} ({row[1]:20s}): {row[2]:2d} jugadores")

        # Por posición
        cur.execute("""
            SELECT posicion, COUNT(*) as cantidad
            FROM research.players_temp
            GROUP BY posicion
            ORDER BY cantidad DESC;
        """)
        print(f"\n⚽ Jugadores por posición:")
        for row in cur.fetchall():
            porcentaje = (row[1] / total) * 100 if total > 0 else 0
            print(f"   • {row[0]:20s}: {row[1]:3d} ({porcentaje:.1f}%)")

        # Estadísticas de edad
        cur.execute("""
            SELECT
                ROUND(AVG(edad), 1) as edad_promedio,
                MIN(edad) as edad_min,
                MAX(edad) as edad_max,
                COUNT(CASE WHEN edad IS NULL THEN 1 END) as sin_edad
            FROM research.players_temp;
        """)
        stats = cur.fetchone()
        print(f"\n📈 Estadísticas de edad:")
        print(f"   • Promedio: {stats[0]} años")
        print(f"   • Mínima: {stats[1]} años")
        print(f"   • Máxima: {stats[2]} años")
        print(f"   • Sin edad: {stats[3]} jugadores")

        # Top 5 goleadores
        cur.execute("""
            SELECT nombre, equipo, posicion, goles
            FROM research.players_temp
            WHERE goles > 0
            ORDER BY goles DESC
            LIMIT 5;
        """)
        print(f"\n🏆 Top 5 goleadores:")
        for i, row in enumerate(cur.fetchall(), 1):
            print(f"   {i}. {row[0]:20s} ({row[2]:15s}) - {row[3]} goles")


def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("📥 CARGA DE DATOS CSV → POSTGRESQL (SPRINT 2)")
    print("=" * 70)

    # 1. Encontrar CSV
    print(f"\n1️⃣  Buscando archivo CSV...")
    csv_file = encontrar_csv_mas_reciente()
    if not csv_file:
        sys.exit(1)

    print(f"   ✅ Encontrado: {csv_file.name}")
    print(f"   📁 Ruta: {csv_file}")

    # 2. Leer CSV
    print(f"\n2️⃣  Leyendo CSV...")
    try:
        df = pd.read_csv(csv_file)
        print(f"   ✅ CSV leído: {len(df)} registros, {len(df.columns)} columnas")
        print(f"   📋 Columnas: {', '.join(df.columns.tolist())}")
    except Exception as e:
        print(f"   ❌ Error al leer CSV: {e}")
        sys.exit(1)

    # 3. Conectar a PostgreSQL
    print(f"\n3️⃣  Conectando a PostgreSQL...")
    conn = conectar_db()
    if not conn:
        sys.exit(1)

    # 4. Verificar que la tabla existe
    print(f"\n4️⃣  Verificando tabla research.players_temp...")
    if not verificar_tabla_existe(conn):
        conn.close()
        sys.exit(1)
    print(f"   ✅ Tabla existe")

    # 5. Limpiar datos
    df = limpiar_datos(df)

    # 6. Cargar datos
    if not cargar_datos(conn, df):
        conn.close()
        sys.exit(1)

    # 7. Verificar carga
    verificar_carga(conn)

    # 8. Cerrar conexión
    conn.close()

    print(f"\n" + "=" * 70)
    print("🎉 CARGA COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print(f"\n💡 Próximos pasos:")
    print(f"   • Puedes consultar los datos con:")
    print(f"     psql -h localhost -p 5433 -U iberscout_user -d iberscout_db")
    print(f"   • Query de ejemplo:")
    print(f"     SELECT * FROM research.players_temp LIMIT 10;")
    print()


if __name__ == "__main__":
    main()
