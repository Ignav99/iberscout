"""
==========================================
SPRINT 5: EXTRACCIÓN MASIVA 3ª RFEF - TODOS LOS GRUPOS Y TEMPORADAS
==========================================
Extrae TODOS los jugadores de 3ª RFEF:
- 18 grupos geográficos
- Múltiples temporadas (2024/25, 2023/24, 2022/23)
- Datos completos: plantilla + minutos + pie dominante

Output: ~27,000 jugadores (18 grupos × 20 equipos × 25 jugadores × 3 temporadas)
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
import random
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# Configuración
OUTPUT_DIR = Path("research/data_samples/analisis_ligas")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DELAY_MIN = 2  # segundos entre jugadores
DELAY_MAX = 4
MAX_REINTENTOS = 2

# Temporadas a extraer
TEMPORADAS = [
    "2024",  # Temporada 2024/25
    "2023",  # Temporada 2023/24
    "2022",  # Temporada 2022/23
]

# Los 18 grupos de 3ª RFEF
GRUPOS_3RFEF = [
    {"numero": 1, "nombre": "Galicia", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo1"},
    {"numero": 2, "nombre": "Asturias-Cantabria", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo2"},
    {"numero": 3, "nombre": "País Vasco", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo3"},
    {"numero": 4, "nombre": "Navarra-La Rioja-Aragón", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo4"},
    {"numero": 5, "nombre": "Cataluña", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo5"},
    {"numero": 6, "nombre": "Comunidad Valenciana Norte", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo6"},
    {"numero": 7, "nombre": "Comunidad Valenciana Sur", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo7"},
    {"numero": 8, "nombre": "Baleares", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo8"},
    {"numero": 9, "nombre": "Murcia", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo9"},
    {"numero": 10, "nombre": "Andalucía Oriental", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo10"},
    {"numero": 11, "nombre": "Andalucía Occidental", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo11"},
    {"numero": 12, "numero": 12, "nombre": "Andalucía Central", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo12"},
    {"numero": 13, "nombre": "Extremadura", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo13"},
    {"numero": 14, "nombre": "Castilla y León", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo14"},
    {"numero": 15, "nombre": "Castilla-La Mancha", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo15"},
    {"numero": 16, "nombre": "Madrid", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo16"},
    {"numero": 17, "nombre": "Canarias", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo17"},
    {"numero": 18, "nombre": "Ceuta-Melilla", "url_base": "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/{temporada}/grupo18"},
]


async def extraer_equipos_grupo(page, url_grupo):
    """Extrae lista de equipos de un grupo"""
    try:
        await page.goto(url_grupo, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(2000)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Buscar tabla de clasificación
        tabla = soup.find('table', class_='table-striped') or soup.find('table')

        if not tabla:
            return []

        # Extraer solo enlaces de equipos de la tabla
        enlaces_equipos = tabla.find_all('a', href=re.compile(r'/equipo/'))

        equipos = []
        equipos_vistos = set()

        for enlace in enlaces_equipos:
            nombre = enlace.get_text(strip=True)
            href = enlace.get('href')

            if not nombre or not href or nombre in equipos_vistos:
                continue

            # Convertir a URL de plantilla
            match = re.search(r'/equipo/(?:info/|plantilla/)?([^/]+)', href)
            if match:
                slug = match.group(1)
                url_plantilla = f"https://es.besoccer.com/equipo/plantilla/{slug}"

                equipos.append({
                    "nombre": nombre,
                    "url": url_plantilla
                })

                equipos_vistos.add(nombre)

        return equipos

    except Exception as e:
        print(f"   ❌ Error extrayendo equipos: {str(e)[:50]}")
        return []


async def extraer_plantilla(page, url_equipo):
    """Extrae plantilla básica de un equipo"""
    try:
        await page.goto(url_equipo, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(1500)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        tabla = soup.find('table')
        if not tabla:
            return []

        filas = tabla.find_all('tr')
        jugadores = []
        posicion_actual = None

        mapeo_posiciones = {
            'Porteros': 'Portero', 'Portero': 'Portero',
            'Defensas': 'Defensa', 'Defensa': 'Defensa',
            'Centrocampistas': 'Centrocampista', 'Centrocampista': 'Centrocampista',
            'Delanteros': 'Delantero', 'Delantero': 'Delantero'
        }

        for fila in filas:
            celdas = fila.find_all(['td', 'th'])
            if len(celdas) == 0:
                continue

            datos = [c.get_text(strip=True) for c in celdas]
            texto_fila = ' '.join(datos)

            # Detectar posición
            for pos_key, pos_valor in mapeo_posiciones.items():
                if pos_key in texto_fila and 'PJ' in texto_fila:
                    posicion_actual = pos_valor
                    break

            # Detectar jugador
            if not datos[0].isdigit():
                continue

            enlace_jugador = fila.find('a', href=lambda x: x and '/jugador/' in x)
            url_jugador = None
            if enlace_jugador:
                href = enlace_jugador.get('href')
                url_jugador = href if href.startswith('http') else f"https://es.besoccer.com{href}"

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

        return jugadores

    except Exception as e:
        return []


async def extraer_minutos_ficha(page, url_jugador):
    """Extrae minutos, pie y nacionalidad de ficha individual"""
    if not url_jugador:
        return {"minutos_jugados": None, "pie_dominante": None, "nacionalidad": None}

    try:
        await page.goto(url_jugador, wait_until="networkidle", timeout=20000)
        await page.wait_for_timeout(1000)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        datos = {"minutos_jugados": None, "pie_dominante": None, "nacionalidad": None}

        # Buscar minutos en tablas
        tablas = soup.find_all('table')
        for tabla in tablas:
            headers = [th.get_text(strip=True).lower() for th in tabla.find_all('th')]

            if 'min' in headers or 'min.' in headers:
                idx_min = next((i for i, h in enumerate(headers) if 'min' in h), None)
                if idx_min:
                    filas = tabla.find_all('tr')
                    for fila in filas[1:]:
                        celdas = fila.find_all('td')
                        if len(celdas) > idx_min:
                            minutos_text = celdas[idx_min].get_text(strip=True).replace('.', '').replace(',', '')
                            if minutos_text.isdigit():
                                datos["minutos_jugados"] = int(minutos_text)
                                break
                    if datos["minutos_jugados"]:
                        break

        # Buscar pie y nacionalidad
        texto = soup.get_text()
        match_pie = re.search(r'[Pp]ie:\s*(Derecho|Izquierdo|Ambidiestro)', texto)
        if match_pie:
            datos["pie_dominante"] = match_pie.group(1)

        match_nac = re.search(r'[Nn]acionalidad:\s*([A-Za-záéíóúñÑ]+)', texto)
        if match_nac:
            datos["nacionalidad"] = match_nac.group(1)

        return datos

    except:
        return {"minutos_jugados": None, "pie_dominante": None, "nacionalidad": None}


async def procesar_equipo(page, equipo_info, grupo_nombre, temporada_str):
    """Procesa un equipo completo"""
    try:
        # Extraer plantilla
        jugadores = await extraer_plantilla(page, equipo_info['url'])

        if not jugadores:
            return []

        # Extraer datos extendidos (limitar para no saturar)
        # Solo extraer minutos de jugadores con >3 partidos para ahorrar tiempo
        for jugador in jugadores:
            if jugador['partidos_jugados'] >= 3 and jugador['url_perfil']:
                await asyncio.sleep(random.uniform(1, 2))
                datos_extra = await extraer_minutos_ficha(page, jugador['url_perfil'])
                jugador.update(datos_extra)
            else:
                jugador.update({"minutos_jugados": None, "pie_dominante": None, "nacionalidad": None})

            # Agregar metadata
            jugador['equipo'] = equipo_info['nombre']
            jugador['liga'] = f"3ª RFEF - {grupo_nombre}"
            jugador['temporada'] = temporada_str
            jugador.pop('url_perfil', None)

        return jugadores

    except Exception as e:
        return []


async def main():
    print("\n" + "🏆"*35)
    print("   EXTRACCIÓN MASIVA 3ª RFEF - TODOS LOS GRUPOS")
    print("🏆"*35 + "\n")

    # Configuración de extracción
    print("⚙️  CONFIGURACIÓN:")
    print(f"   Grupos: {len(GRUPOS_3RFEF)}")
    print(f"   Temporadas: {len(TEMPORADAS)}")
    print(f"   Equipos estimados: ~360 ({len(GRUPOS_3RFEF)} × ~20)")
    print(f"   Jugadores estimados: ~9,000 por temporada, ~27,000 total")
    print(f"   Tiempo estimado: 6-10 horas\n")

    confirmar = input("⚠️  Esta es una extracción MASIVA. ¿Continuar? (s/n): ")
    if confirmar.lower() != 's':
        print("❌ Extracción cancelada")
        return

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True, timeout=60000)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-ES'
        )
        page = await context.new_page()

        todos_jugadores = []

        # Procesar por temporada
        for temporada in TEMPORADAS:
            temporada_str = f"{temporada}/{int(temporada[-2:])+1}"
            print(f"\n{'='*70}")
            print(f"📅 TEMPORADA: {temporada_str}")
            print(f"{'='*70}\n")

            # Procesar por grupo
            for grupo in GRUPOS_3RFEF:
                url_grupo = grupo['url_base'].format(temporada=temporada)
                print(f"\n🗺️  Grupo {grupo['numero']}: {grupo['nombre']}")

                # Extraer equipos del grupo
                equipos = await extraer_equipos_grupo(page, url_grupo)
                print(f"   📋 Equipos encontrados: {len(equipos)}")

                if not equipos:
                    print(f"   ⚠️  Sin equipos, saltando...")
                    continue

                await asyncio.sleep(3)

                # Procesar cada equipo
                with tqdm(total=len(equipos), desc=f"   Grupo {grupo['numero']}", unit="equipo") as pbar:
                    for equipo in equipos:
                        await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

                        jugadores = await procesar_equipo(page, equipo, grupo['nombre'], temporada_str)
                        todos_jugadores.extend(jugadores)

                        pbar.set_postfix(jugadores=len(todos_jugadores))
                        pbar.update(1)

        await browser.close()

        # Guardar resultados
        print(f"\n{'='*70}")
        print(f"💾 GUARDANDO RESULTADOS")
        print(f"{'='*70}\n")

        df = pd.DataFrame(todos_jugadores)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = OUTPUT_DIR / f"3rfef_completa_{timestamp}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        json_path = OUTPUT_DIR / f"3rfef_completa_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(todos_jugadores, f, indent=2, ensure_ascii=False)

        print(f"✅ CSV: {csv_path.name}")
        print(f"✅ JSON: {json_path.name}")

        print(f"\n{'='*70}")
        print(f"🎉 ¡EXTRACCIÓN COMPLETADA!")
        print(f"{'='*70}\n")
        print(f"Total jugadores: {len(df)}")
        print(f"Temporadas: {df['temporada'].nunique()}")
        print(f"Equipos: {df['equipo'].nunique()}")


if __name__ == "__main__":
    asyncio.run(main())
