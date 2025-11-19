"""
==========================================
IBERSCOUT - TEST SIMPLE DE POSTGRESQL
==========================================
"""

import psycopg2
import sys

print("\n" + "="*70)
print("🔍 DIAGNÓSTICO DE POSTGRESQL - TEST SIMPLE")
print("="*70 + "\n")

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'iberscout_db',
    'user': 'iberscout_user',
    'password': 'TIZ@voltio999'
}

print("�� CONFIGURACIÓN:")
print(f"   Host: {DB_CONFIG['host']}")
print(f"   Puerto: {DB_CONFIG['port']}")
print(f"   Base de datos: {DB_CONFIG['database']}")
print(f"   Usuario: {DB_CONFIG['user']}")
print(f"   Password: {'*' * len(DB_CONFIG['password'])}")
print("\n" + "-"*70 + "\n")

print("🧪 TEST 1: Intentando conexión...")
try:
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        connect_timeout=5
    )
    print("✅ CONEXIÓN EXITOSA\n")
    
except psycopg2.OperationalError as e:
    print(f"❌ ERROR: {e}\n")
    sys.exit(1)

print("🧪 TEST 2: Verificando versión...")
cursor = conn.cursor()
cursor.execute("SELECT version();")
version = cursor.fetchone()[0]
print(f"✅ {version.split(',')[0]}\n")

print("🧪 TEST 3: Creando tabla de prueba...")
cursor.execute("CREATE SCHEMA IF NOT EXISTS research;")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS research.test_iberscout (
        id SERIAL PRIMARY KEY,
        mensaje TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
cursor.execute("""
    INSERT INTO research.test_iberscout (mensaje) 
    VALUES ('✅ IberScout conectado correctamente!');
""")
cursor.execute("SELECT * FROM research.test_iberscout ORDER BY id DESC LIMIT 1;")
resultado = cursor.fetchone()
conn.commit()

print(f"✅ Tabla creada - ID: {resultado[0]}, Mensaje: {resultado[1]}\n")

cursor.close()
conn.close()

print("="*70)
print("🎉 POSTGRESQL FUNCIONANDO CORRECTAMENTE")
print("="*70 + "\n")
