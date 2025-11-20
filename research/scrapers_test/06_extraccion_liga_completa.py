"""
==========================================
SPRINT 4: EXTRACCIÓN MASIVA - LIGA COMPLETA
==========================================
Scraping de TODOS los equipos de 3ª RFEF con delays, reintentos y progreso
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import json
import random
import time
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# Rutas
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "research" / "data_samples" / "analisis_ligas"
EQUIPOS_FILE = OUTPUT_DIR / "equipos_3rfef_grupo1.json"

# Configuración
MAX_REINTENTOS = 3
DELAY_MIN = 3  # segundos
DELAY_MAX = 7  # segundos


def cargar_equipos():
    """Carga la lista de equipos desde el JSON generado por extraer_equipos_liga.py"""
    if not EQUIPOS_FILE.exists():
        print(f"❌ Error: No se encontró {EQUIPOS_FILE}")
        print(f"\n💡 SOLUCIÓN:")
        print(f"   1. Ejecuta primero: python research/scrapers_test/extraer_equipos_liga.py")
        print(f"   2. Ese script generará la lista de equipos")
        print(f"   3. Luego ejecuta este script nuevamente")
        return None

    with open(EQUIPOS_FILE, 'r', encoding='utf-8') as f:
        equipos = json.load(f)

    return equipos


async def extraer_equipo_con_reintentos(equipo_info, browser, intento=1):
    """Extrae jugadores de un equipo con sistema de reintentos"""
    nombre = equipo_info['nombre']
    url = equipo_info['url']

    try:
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-ES'
        )

        page = await context.new_page()
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(2000)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        tablas = soup.find_all('table')

        if not tablas:
            print(f"   ⚠️  No se encontraron tablas")
            await context.close()
            return []

        tabla = tablas[0]
        filas = tabla.find_all('tr')

        jugadores = []
        posicion_actual = None

        mapeo_posiciones = {
            'Porteros': 'Portero',
            'Portero': 'Portero',
            'Defensas': 'Defensa',
            'Defensa': 'Defensa',
            'Centrocampistas': 'Centrocampista',
            'Centrocampista': 'Centrocampista',
            'Delanteros': 'Delantero',
            'Delantero': 'Delantero'
        }

        for fila in filas:
            celdas = fila.find_all(['td', 'th'])
            if len(celdas) == 0:
                continue

            datos = [c.get_text(strip=True) for c in celdas]
            texto_fila = ' '.join(datos)

            # Detectar fila de posición
            for pos_key, pos_valor in mapeo_posiciones.items():
                if pos_key in texto_fila and 'PJ' in texto_fila:
                    posicion_actual = pos_valor
                    break

            # Detectar fila de jugador
            if not datos[0].isdigit():
                continue

            jugador = {
                "dorsal": int(datos[0]) if datos[0].isdigit() else None,
                "nombre": datos[2] if len(datos) > 2 else "",
                "posicion": posicion_actual,
                "partidos_jugados": int(datos[4]) if len(datos) > 4 and datos[4].isdigit() else 0,
                "partidos_titular": int(datos[5]) if len(datos) > 5 and datos[5].isdigit() else 0,
                "goles": int(datos[6]) if len(datos) > 6 and datos[6].isdigit() else 0,
                "asistencias": int(datos[7]) if len(datos) > 7 and datos[7].isdigit() else 0,
                "edad": int(datos[9]) if len(datos) > 9 and datos[9].isdigit() else None,
                "equipo": nombre,
                "liga": "3ª RFEF"
            }

            jugadores.append(jugador)

        await context.close()
        return jugadores

    except Exception as e:
        print(f"   ❌ Error (intento {intento}/{MAX_REINTENTOS}): {str(e)[:100]}")

        try:
            await context.close()
        except:
            pass

        # Reintentar si no hemos llegado al máximo
        if intento < MAX_REINTENTOS:
            print(f"   🔄 Reintentando en 5 segundos...")
            await asyncio.sleep(5)
            return await extraer_equipo_con_reintentos(equipo_info, browser, intento + 1)
        else:
            print(f"   ❌ Falló después de {MAX_REINTENTOS} intentos")
            return None


async def main():
    """Función principal"""
    print("\n" + "🏆"*35)
    print("   SPRINT 4: EXTRACCIÓN MASIVA - LIGA COMPLETA")
    print("🏆"*35 + "\n")

    # Cargar equipos
    equipos = cargar_equipos()
    if not equipos:
        return

    print(f"📊 Equipos a scrapear: {len(equipos)}")
    print(f"⏱️  Tiempo estimado: {len(equipos) * 5} - {len(equipos) * 10} segundos")
    print(f"🎯 Objetivo: ~{len(equipos) * 25} jugadores\n")

    input("Presiona ENTER para comenzar...")

    # Lanzar Firefox
    async with async_playwright() as p:
        print("\n🦊 Lanzando Firefox...")
        browser = await p.firefox.launch(headless=True, timeout=60000)
        print("✅ Firefox listo\n")

        todos_jugadores = []
        equipos_exitosos = 0
        equipos_fallidos = []

        # Procesar cada equipo con barra de progreso
        with tqdm(total=len(equipos), desc="Scraping", unit="equipo") as pbar:
            for i, equipo_info in enumerate(equipos, 1):
                nombre = equipo_info['nombre']

                pbar.set_description(f"🔍 {nombre[:30]}")

                # Delay aleatorio (excepto en el primero)
                if i > 1:
                    delay = random.uniform(DELAY_MIN, DELAY_MAX)
                    await asyncio.sleep(delay)

                # Extraer jugadores
                jugadores = await extraer_equipo_con_reintentos(equipo_info, browser)

                if jugadores is not None:
                    todos_jugadores.extend(jugadores)
                    equipos_exitosos += 1
                    pbar.set_postfix(exitosos=equipos_exitosos, jugadores=len(todos_jugadores))
                else:
                    equipos_fallidos.append(nombre)

                pbar.update(1)

        await browser.close()
        print("\n✅ Firefox cerrado")

    # RESUMEN
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN DE EXTRACCIÓN")
    print(f"{'='*70}\n")

    print(f"✅ Equipos exitosos: {equipos_exitosos}/{len(equipos)}")
    print(f"✅ Total jugadores: {len(todos_jugadores)}")

    if equipos_fallidos:
        print(f"\n❌ Equipos que fallaron ({len(equipos_fallidos)}):")
        for equipo in equipos_fallidos:
            print(f"   • {equipo}")

    if len(todos_jugadores) == 0:
        print("\n❌ No se extrajeron jugadores")
        return

    # Estadísticas rápidas
    df = pd.DataFrame(todos_jugadores)

    print(f"\n📈 ESTADÍSTICAS RÁPIDAS:")
    print(f"   Edad promedio: {df['edad'].mean():.1f} años")
    print(f"   Jugadores con edad: {df['edad'].notna().sum()}/{len(df)}")

    print(f"\n   Jugadores por posición:")
    posiciones = df['posicion'].value_counts()
    for pos, count in posiciones.items():
        if pd.notna(pos):
            print(f"      {pos}: {count}")

    # Guardar datos
    print(f"\n💾 Guardando datos...")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    csv_path = OUTPUT_DIR / f"liga_completa_{timestamp}.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"   📄 CSV: {csv_path.name}")

    json_path = OUTPUT_DIR / f"liga_completa_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(todos_jugadores, f, indent=2, ensure_ascii=False)
    print(f"   📄 JSON: {json_path.name}")

    print(f"\n🎉 ¡EXTRACCIÓN COMPLETADA!")
    print(f"\n📝 Próximos pasos:")
    print(f"   1. Cargar datos a PostgreSQL:")
    print(f"      python research/scrapers_test/03_load_to_db.py")
    print(f"   2. Verificar duplicados:")
    print(f"      python research/scrapers_test/05_fuzzy_matching_bd.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
