"""
==========================================
SPRINT 3: FUZZY MATCHING - APLICAR A BD
==========================================
Busca jugadores duplicados en los 110 registros de PostgreSQL
"""

import psycopg2
from thefuzz import fuzz
import pandas as pd

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'iberscout_db',
    'user': 'iberscout_user',
    'password': 'TIZ@voltio999'
}

# Configuración del algoritmo (basado en resultados del test 04_fuzzy_matching_test.py)
# MEJOR CONFIGURACIÓN: partial_ratio con umbral 70% (F1-Score: 0.94)
ALGORITMO = fuzz.partial_ratio
UMBRAL = 70  # Umbral óptimo según validación

print("\n" + "="*70)
print("🔍 SPRINT 3: FUZZY MATCHING - ANÁLISIS DE BD")
print("="*70 + "\n")

# ==============================================================================
# CONECTAR A POSTGRESQL
# ==============================================================================

print("1️⃣  Conectando a PostgreSQL...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    print(f"   ✅ Conectado a {DB_CONFIG['database']}\n")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"\n💡 Verifica:")
    print(f"   1. Docker está corriendo: docker-compose ps")
    print(f"   2. PostgreSQL está levantado\n")
    exit(1)

# ==============================================================================
# EXTRAER JUGADORES DE LA BD
# ==============================================================================

print("2️⃣  Extrayendo jugadores de research.players_temp...")

query = """
SELECT id, nombre, equipo, posicion, edad, liga
FROM research.players_temp
ORDER BY nombre;
"""

try:
    df = pd.read_sql_query(query, conn)
    print(f"   ✅ {len(df)} jugadores extraídos\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    conn.close()
    exit(1)

# ==============================================================================
# BUSCAR DUPLICADOS POTENCIALES
# ==============================================================================

print(f"3️⃣  Buscando duplicados potenciales...")
print(f"   Algoritmo: {ALGORITMO.__name__}")
print(f"   Umbral: {UMBRAL}%\n")

duplicados_potenciales = []

# Comparar cada jugador con todos los demás
for i, row1 in df.iterrows():
    for j, row2 in df.iterrows():
        # No comparar consigo mismo
        if i >= j:
            continue

        # Calcular similitud
        similitud = ALGORITMO(row1['nombre'], row2['nombre'])

        # Si la similitud supera el umbral, es un duplicado potencial
        if similitud >= UMBRAL:
            duplicados_potenciales.append({
                "id1": row1['id'],
                "nombre1": row1['nombre'],
                "equipo1": row1['equipo'],
                "posicion1": row1['posicion'],
                "edad1": row1['edad'],
                "id2": row2['id'],
                "nombre2": row2['nombre'],
                "equipo2": row2['equipo'],
                "posicion2": row2['posicion'],
                "edad2": row2['edad'],
                "similitud": similitud,
            })

print(f"   ✅ Búsqueda completada\n")

# ==============================================================================
# ANÁLISIS DE RESULTADOS
# ==============================================================================

print("="*70)
print("📊 RESULTADOS DEL ANÁLISIS")
print("="*70 + "\n")

if len(duplicados_potenciales) == 0:
    print("✅ NO SE ENCONTRARON DUPLICADOS POTENCIALES")
    print(f"   Todos los {len(df)} jugadores tienen nombres suficientemente diferentes")
    print(f"   (similitud < {UMBRAL}%)\n")
else:
    print(f"⚠️  SE ENCONTRARON {len(duplicados_potenciales)} DUPLICADOS POTENCIALES:\n")

    for i, dup in enumerate(duplicados_potenciales, 1):
        print(f"{'─'*70}")
        print(f"Caso #{i} - Similitud: {dup['similitud']}%")
        print(f"{'─'*70}")
        print(f"  Jugador A:")
        print(f"    ID: {dup['id1']}")
        print(f"    Nombre: {dup['nombre1']}")
        print(f"    Equipo: {dup['equipo1']}")
        print(f"    Posición: {dup['posicion1']}")
        print(f"    Edad: {dup['edad1']}")
        print(f"")
        print(f"  Jugador B:")
        print(f"    ID: {dup['id2']}")
        print(f"    Nombre: {dup['nombre2']}")
        print(f"    Equipo: {dup['equipo2']}")
        print(f"    Posición: {dup['posicion2']}")
        print(f"    Edad: {dup['edad2']}")
        print(f"")

        # Análisis automático
        mismo_equipo = dup['equipo1'] == dup['equipo2']
        misma_posicion = dup['posicion1'] == dup['posicion2']
        misma_edad = dup['edad1'] == dup['edad2']

        if mismo_equipo and misma_posicion:
            print(f"  🚨 ALERTA: Mismo equipo y posición → Probablemente duplicado REAL")
        elif mismo_equipo:
            print(f"  ⚠️  Mismo equipo pero diferente posición → Revisar manualmente")
        else:
            print(f"  ✅ Equipos diferentes → Probablemente jugadores distintos")

        print()

# ==============================================================================
# ESTADÍSTICAS GENERALES
# ==============================================================================

print("="*70)
print("📈 ESTADÍSTICAS GENERALES")
print("="*70 + "\n")

print(f"Total de jugadores analizados: {len(df)}")
print(f"Comparaciones realizadas: {len(df) * (len(df) - 1) // 2}")
print(f"Duplicados potenciales encontrados: {len(duplicados_potenciales)}")
print(f"Tasa de duplicados: {len(duplicados_potenciales) / len(df) * 100:.2f}%")

if len(duplicados_potenciales) > 0:
    # Contar duplicados por equipo
    equipos_con_duplicados = set()
    for dup in duplicados_potenciales:
        if dup['equipo1'] == dup['equipo2']:
            equipos_con_duplicados.add(dup['equipo1'])

    print(f"\nEquipos con duplicados potenciales: {len(equipos_con_duplicados)}")
    if equipos_con_duplicados:
        for equipo in equipos_con_duplicados:
            print(f"   • {equipo}")

# ==============================================================================
# RECOMENDACIONES
# ==============================================================================

print(f"\n{'='*70}")
print("💡 RECOMENDACIONES")
print(f"{'='*70}\n")

if len(duplicados_potenciales) == 0:
    print("✅ Los datos actuales NO tienen duplicados evidentes")
    print("✅ Puedes continuar al Sprint 4 (Extracción masiva)")
else:
    print("⚠️  ACCIÓN REQUERIDA:")
    print()
    print(f"1. Revisa manualmente los {len(duplicados_potenciales)} casos listados arriba")
    print("2. Para cada caso, decide:")
    print("   • Si SON el mismo jugador → Eliminar uno y quedarte con el mejor")
    print("   • Si son DIFERENTES → Ajustar el umbral o ignorar")
    print()
    print("3. Query útil para eliminar duplicado:")
    print("   DELETE FROM research.players_temp WHERE id = X;")
    print()
    print("4. Si hay muchos falsos positivos, considera:")
    print(f"   • Aumentar el umbral (ej: de {UMBRAL}% a {UMBRAL + 5}%)")
    print("   • Usar información adicional (edad, equipo) para filtrar")

# ==============================================================================
# GUARDAR RESULTADOS (OPCIONAL)
# ==============================================================================

if len(duplicados_potenciales) > 0:
    print(f"\n{'='*70}")
    print("💾 GUARDAR RESULTADOS")
    print(f"{'='*70}\n")

    df_duplicados = pd.DataFrame(duplicados_potenciales)
    output_file = "research/data_samples/analisis_ligas/duplicados_potenciales.csv"

    try:
        df_duplicados.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ Resultados guardados en: {output_file}")
        print(f"   Puedes abrirlo con Excel o cualquier editor CSV\n")
    except Exception as e:
        print(f"⚠️  No se pudo guardar el archivo: {e}\n")

# ==============================================================================
# CERRAR CONEXIÓN
# ==============================================================================

conn.close()

print("="*70)
print("🎉 ANÁLISIS COMPLETADO")
print("="*70 + "\n")
