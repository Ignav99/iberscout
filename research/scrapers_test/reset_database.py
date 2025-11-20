"""
==========================================
SPRINT 5: RESET DE BASE DE DATOS
==========================================
Limpia completamente la tabla research.players antes de extracción definitiva

IMPORTANTE: Este script ELIMINA TODOS LOS DATOS
Solo ejecutar cuando estés SEGURO de que quieres empezar de cero
"""

import psycopg2
from datetime import datetime

# Configuración de conexión
DB_CONFIG = {
    'dbname': 'iberscout_db',
    'user': 'iberscout_user',
    'password': 'iberscout_pass',
    'host': 'localhost',
    'port': '5433'
}


def confirmar_reset():
    """Pide confirmación antes de eliminar datos"""
    print("\n" + "="*70)
    print("⚠️  ⚠️  ⚠️   RESET DE BASE DE DATOS   ⚠️  ⚠️  ⚠️")
    print("="*70 + "\n")

    print("Este script eliminará TODOS los datos de research.players")
    print("Esta acción NO se puede deshacer.\n")

    confirmar1 = input("¿Estás seguro de que quieres continuar? (escribe 'SI'): ")

    if confirmar1 != 'SI':
        print("\n❌ Reset cancelado")
        return False

    print("\n⚠️  ÚLTIMA ADVERTENCIA:")
    print("Todos los jugadores, estadísticas y datos se eliminarán permanentemente.\n")

    confirmar2 = input("Confirma escribiendo 'ELIMINAR': ")

    if confirmar2 != 'ELIMINAR':
        print("\n❌ Reset cancelado")
        return False

    return True


def conectar_db():
    """Conecta a PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"\n❌ Error conectando a PostgreSQL: {e}")
        print("\nVerifica que:")
        print("  1. Docker está corriendo")
        print("  2. El contenedor de PostgreSQL está activo")
        print("  3. Las credenciales son correctas")
        return None


def obtener_estadisticas(cursor):
    """Obtiene estadísticas actuales de la BD"""
    try:
        # Total jugadores
        cursor.execute("SELECT COUNT(*) FROM research.players;")
        total = cursor.fetchone()[0]

        # Por liga
        cursor.execute("""
            SELECT liga, COUNT(*) as count
            FROM research.players
            GROUP BY liga
            ORDER BY count DESC;
        """)
        por_liga = cursor.fetchall()

        # Por temporada
        cursor.execute("""
            SELECT temporada, COUNT(*) as count
            FROM research.players
            GROUP BY temporada
            ORDER BY temporada DESC;
        """)
        por_temporada = cursor.fetchall()

        return {
            'total': total,
            'por_liga': por_liga,
            'por_temporada': por_temporada
        }

    except Exception as e:
        print(f"⚠️  No se pudieron obtener estadísticas: {e}")
        return None


def reset_tabla(conn):
    """Elimina todos los datos y resetea secuencias"""
    cursor = conn.cursor()

    try:
        print("\n📊 Estadísticas ANTES del reset:")
        print("="*70)

        stats = obtener_estadisticas(cursor)

        if stats:
            print(f"\nTotal jugadores: {stats['total']}")

            if stats['por_liga']:
                print(f"\nPor liga:")
                for liga, count in stats['por_liga']:
                    print(f"  {liga}: {count}")

            if stats['por_temporada']:
                print(f"\nPor temporada:")
                for temp, count in stats['por_temporada']:
                    print(f"  {temp}: {count}")

            print("\n" + "="*70)

        # TRUNCATE (más rápido que DELETE)
        print("\n🗑️  Ejecutando TRUNCATE...")
        cursor.execute("TRUNCATE TABLE research.players RESTART IDENTITY CASCADE;")

        # Commit
        conn.commit()

        print("✅ Tabla truncada exitosamente")

        # Verificar
        cursor.execute("SELECT COUNT(*) FROM research.players;")
        count_after = cursor.fetchone()[0]

        if count_after == 0:
            print("✅ Verificación: Tabla vacía")
        else:
            print(f"⚠️  Advertencia: Aún hay {count_after} registros")

        cursor.close()

        return True

    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"\n❌ Error durante reset: {e}")
        return False


def main():
    print("\n🔧 IBERSCOUT - Reset de Base de Datos")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Confirmar
    if not confirmar_reset():
        return

    # Conectar
    print("\n🔌 Conectando a PostgreSQL...")
    conn = conectar_db()

    if not conn:
        return

    print("✅ Conexión establecida")

    # Reset
    success = reset_tabla(conn)

    # Cerrar conexión
    conn.close()
    print("\n🔌 Conexión cerrada")

    # Resumen
    if success:
        print("\n" + "="*70)
        print("✅ RESET COMPLETADO")
        print("="*70 + "\n")
        print("La tabla research.players está ahora vacía.")
        print("Próximo paso:")
        print("  1. Ejecutar extracción masiva:")
        print("     python research/scrapers_test/13_extraccion_3rfef_completa.py")
        print("  2. Cargar datos a PostgreSQL")
        print()
    else:
        print("\n" + "="*70)
        print("❌ RESET FALLIDO")
        print("="*70 + "\n")
        print("Revisa los errores arriba y vuelve a intentar.")
        print()


if __name__ == "__main__":
    main()
