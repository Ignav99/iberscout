"""
==========================================
SPRINT 5: EXTRACCIÓN COMPLETA CON MINUTOS JUGADOS
==========================================
Extrae datos de BeSoccer combinando:
1. Tabla de plantilla → partidos, goles, asistencias, edad
2. Ficha individual → minutos jugados, pie dominante, nacionalidad

Este script es el DEFINITIVO para 3ª RFEF v1
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from datetime import datetime
from pathlib import Path

# Configuración
EQUIPO_URL = "https://es.besoccer.com/equipo/plantilla/bergantinos"
EQUIPO_NOMBRE = "Bergantiños FC"
TEMPORADA = "2024/25"
LIGA = "3ª RFEF"

OUTPUT_DIR = Path("research/data_samples/analisis_ligas")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def extraer_plantilla(page, url_equipo):
    """Extrae datos básicos de la tabla de plantilla"""
    print(f"📊 Extrayendo plantilla de {url_equipo}...")

    await page.goto(url_equipo, wait_until="networkidle", timeout=60000)
    await page.wait_for_timeout(2000)

    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')

    tabla = soup.find('table')
    if not tabla:
        print("❌ No se encontró tabla de plantilla")
        return []

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

        # Buscar enlace al perfil del jugador
        enlace_jugador = fila.find('a', href=lambda x: x and '/jugador/' in x)
        url_jugador = None
        if enlace_jugador:
            href = enlace_jugador.get('href')
            if href.startswith('http'):
                url_jugador = href
            else:
                url_jugador = "https://es.besoccer.com" + href

        jugador = {
            "dorsal": int(datos[0]) if datos[0].isdigit() else None,
            "nombre": datos[2] if len(datos) > 2 else "",
            "posicion": posicion_actual,
            "partidos_jugados": int(datos[4]) if len(datos) > 4 and datos[4].isdigit() else 0,
            "partidos_titular": int(datos[5]) if len(datos) > 5 and datos[5].isdigit() else 0,
            "goles": int(datos[6]) if len(datos) > 6 and datos[6].isdigit() else 0,
            "asistencias": int(datos[7]) if len(datos) > 7 and datos[7].isdigit() else 0,
            "edad": int(datos[9]) if len(datos) > 9 and datos[9].isdigit() else None,
            "url_perfil": url_jugador
        }

        jugadores.append(jugador)

    print(f"✅ Extraídos {len(jugadores)} jugadores de plantilla")
    return jugadores


async def extraer_minutos_ficha(page, url_jugador, nombre):
    """Extrae minutos jugados, pie dominante y nacionalidad de ficha individual"""
    if not url_jugador:
        print(f"   ⚠️  {nombre}: Sin URL de perfil")
        return {"minutos_jugados": None, "pie_dominante": None, "nacionalidad": None}

    print(f"   🔍 {nombre}: Extrayendo datos extendidos...")

    try:
        await page.goto(url_jugador, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(1500)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        datos_extra = {
            "minutos_jugados": None,
            "pie_dominante": None,
            "nacionalidad": None
        }

        # Buscar tablas con headers específicos
        tablas = soup.find_all('table')

        for tabla in tablas:
            headers = [th.get_text(strip=True) for th in tabla.find_all('th')]
            headers_lower = [h.lower() for h in headers]

            # Tabla con minutos (buscar 'MIN' o 'Min.')
            if 'min' in headers_lower or 'min.' in headers_lower:
                # Buscar índice de columna MIN
                idx_min = None
                for i, h in enumerate(headers_lower):
                    if 'min' in h:
                        idx_min = i
                        break

                if idx_min is not None:
                    # Buscar primera fila de datos (temporada actual)
                    filas = tabla.find_all('tr')
                    for fila in filas[1:]:  # Saltar header
                        celdas = fila.find_all('td')
                        if len(celdas) > idx_min:
                            minutos_text = celdas[idx_min].get_text(strip=True)
                            # Limpiar formato (puede venir con puntos: "1.234" → 1234)
                            minutos_text = minutos_text.replace('.', '').replace(',', '')
                            if minutos_text.isdigit():
                                datos_extra["minutos_jugados"] = int(minutos_text)
                                break

        # Buscar pie dominante y nacionalidad en texto
        texto_completo = soup.get_text()

        # Pie dominante
        if 'Pie:' in texto_completo or 'pie:' in texto_completo:
            # Buscar patrón "Pie: Derecho/Izquierdo/Ambidiestro"
            match = re.search(r'[Pp]ie:\s*(Derecho|Izquierdo|Ambidiestro)', texto_completo)
            if match:
                datos_extra["pie_dominante"] = match.group(1)

        # Nacionalidad (menos confiable, puede no estar)
        if 'nacionalidad' in texto_completo.lower():
            match = re.search(r'[Nn]acionalidad:\s*([A-Za-záéíóúñÑ]+)', texto_completo)
            if match:
                datos_extra["nacionalidad"] = match.group(1)

        # Log resultado
        minutos_str = datos_extra["minutos_jugados"] if datos_extra["minutos_jugados"] is not None else "N/A"
        pie_str = datos_extra["pie_dominante"] if datos_extra["pie_dominante"] else "N/A"
        print(f"      → Minutos: {minutos_str}, Pie: {pie_str}")

        return datos_extra

    except Exception as e:
        print(f"   ❌ {nombre}: Error extrayendo ficha - {str(e)[:50]}")
        return {"minutos_jugados": None, "pie_dominante": None, "nacionalidad": None}


async def main():
    print("\n" + "="*70)
    print("🏆 SPRINT 5: EXTRACCIÓN COMPLETA CON MINUTOS")
    print("="*70 + "\n")

    print(f"🎯 Equipo: {EQUIPO_NOMBRE}")
    print(f"📅 Temporada: {TEMPORADA}")
    print(f"🏆 Liga: {LIGA}\n")

    async with async_playwright() as p:
        print("🦊 Lanzando Firefox...")
        browser = await p.firefox.launch(headless=True, timeout=60000)

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-ES'
        )

        page = await context.new_page()

        # PASO 1: Extraer plantilla
        jugadores = await extraer_plantilla(page, EQUIPO_URL)

        if not jugadores:
            print("❌ No se pudieron extraer jugadores")
            await browser.close()
            return

        # PASO 2: Extraer datos extendidos de cada jugador
        print(f"\n{'='*70}")
        print(f"📊 EXTRAYENDO DATOS EXTENDIDOS ({len(jugadores)} jugadores)")
        print(f"{'='*70}\n")

        for i, jugador in enumerate(jugadores, 1):
            print(f"[{i}/{len(jugadores)}] {jugador['nombre']}:")

            # Delay entre jugadores
            if i > 1:
                await asyncio.sleep(2)

            datos_extra = await extraer_minutos_ficha(
                page,
                jugador['url_perfil'],
                jugador['nombre']
            )

            # Agregar datos extendidos al jugador
            jugador.update(datos_extra)

            # Agregar metadata
            jugador['equipo'] = EQUIPO_NOMBRE
            jugador['liga'] = LIGA
            jugador['temporada'] = TEMPORADA

            # Limpiar campo temporal
            jugador.pop('url_perfil', None)

        await browser.close()
        print("\n✅ Firefox cerrado")

        # PASO 3: Análisis y guardado
        print(f"\n{'='*70}")
        print(f"📊 RESUMEN DE EXTRACCIÓN")
        print(f"{'='*70}\n")

        df = pd.DataFrame(jugadores)

        print(f"✅ Total jugadores: {len(df)}")
        print(f"   Edad promedio: {df['edad'].mean():.1f} años")
        print(f"   Con minutos: {df['minutos_jugados'].notna().sum()}/{len(df)}")
        print(f"   Con pie dominante: {df['pie_dominante'].notna().sum()}/{len(df)}")
        print(f"   Con nacionalidad: {df['nacionalidad'].notna().sum()}/{len(df)}")

        print(f"\n   Jugadores por posición:")
        for pos, count in df['posicion'].value_counts().items():
            print(f"      {pos}: {count}")

        # Guardar datos
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        csv_path = OUTPUT_DIR / f"extraccion_completa_{timestamp}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n💾 CSV guardado: {csv_path.name}")

        json_path = OUTPUT_DIR / f"extraccion_completa_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(jugadores, f, indent=2, ensure_ascii=False)
        print(f"💾 JSON guardado: {json_path.name}")

        print(f"\n🎉 ¡EXTRACCIÓN COMPLETADA!")
        print(f"\n📝 Próximos pasos:")
        print(f"   1. Validar datos en CSV")
        print(f"   2. Ejecutar script multi-grupo multi-temporada")
        print(f"   3. Cargar a PostgreSQL con 02_create_players_v1.sql")
        print()


if __name__ == "__main__":
    asyncio.run(main())
