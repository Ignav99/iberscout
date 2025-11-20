"""
==========================================
SPRINT 5: EXPLORACIÓN - BeSoccer Fichas Individuales
==========================================
Objetivo: Investigar QUÉ datos adicionales tienen las fichas individuales de jugadores
Comparar con los datos que ya extraemos de la tabla de plantilla
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime

# CONFIGURACIÓN: Cambia estos valores para probar con diferentes equipos
EQUIPO_URL = "https://es.besoccer.com/equipo/plantilla/bergantinos"
EQUIPO_NOMBRE = "Bergantiños FC"
LIMITE_JUGADORES = 3  # Solo probar con 3 jugadores para no saturar


async def extraer_datos_tabla_plantilla(page):
    """Extrae datos básicos de la tabla de plantilla (lo que ya hacemos)"""
    print("📊 Extrayendo datos de tabla de plantilla...")

    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')

    tabla = soup.find('table')
    if not tabla:
        print("❌ No se encontró tabla de plantilla")
        return []

    filas = tabla.find_all('tr')
    jugadores = []

    for fila in filas:
        celdas = fila.find_all(['td', 'th'])
        if len(celdas) == 0 or not celdas[0].get_text(strip=True).isdigit():
            continue

        datos = [c.get_text(strip=True) for c in celdas]

        # Buscar enlace al perfil del jugador
        enlace_jugador = fila.find('a', href=lambda x: x and '/jugador/' in x)
        url_jugador = None
        if enlace_jugador:
            url_jugador = "https://es.besoccer.com" + enlace_jugador.get('href')

        jugador = {
            "dorsal": datos[0] if len(datos) > 0 else None,
            "nombre": datos[2] if len(datos) > 2 else None,
            "partidos_jugados": datos[4] if len(datos) > 4 else None,
            "goles": datos[6] if len(datos) > 6 else None,
            "edad": datos[9] if len(datos) > 9 else None,
            "url_perfil": url_jugador
        }

        jugadores.append(jugador)

    print(f"✅ Encontrados {len(jugadores)} jugadores en tabla")
    return jugadores


async def extraer_datos_ficha_individual(page, url_jugador, nombre):
    """Extrae TODOS los datos disponibles en la ficha individual del jugador"""
    print(f"\n🔍 Explorando ficha individual: {nombre}")
    print(f"   URL: {url_jugador}")

    try:
        await page.goto(url_jugador, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # ESTRATEGIA: Extraer TODO el HTML y analizar qué hay disponible
        datos_ficha = {
            "nombre": nombre,
            "url": url_jugador,
            "datos_encontrados": {}
        }

        # 1. Buscar sección de información personal
        print("   Buscando datos personales...")

        # Buscar todos los elementos que puedan contener datos
        # (altura, peso, nacionalidad, fecha nacimiento, pie dominante)
        info_sections = soup.find_all(['div', 'span', 'p'], class_=lambda x: x and ('info' in x.lower() or 'data' in x.lower()))

        # 2. Buscar tablas de estadísticas
        print("   Buscando tablas de estadísticas...")
        tablas = soup.find_all('table')

        datos_ficha["num_tablas_encontradas"] = len(tablas)
        datos_ficha["tablas"] = []

        for idx, tabla in enumerate(tablas):
            print(f"   📋 Tabla {idx+1}:")
            headers = [th.get_text(strip=True) for th in tabla.find_all('th')]
            print(f"      Headers: {headers}")

            # Guardar primera fila de datos como ejemplo
            primera_fila = tabla.find('tr')
            if primera_fila:
                celdas = [td.get_text(strip=True) for td in primera_fila.find_all('td')]
                print(f"      Ejemplo datos: {celdas[:5]}...")

            datos_ficha["tablas"].append({
                "headers": headers,
                "num_filas": len(tabla.find_all('tr'))
            })

        # 3. Buscar datos específicos por palabras clave
        print("   Buscando campos específicos...")

        texto_completo = soup.get_text()

        campos_buscar = [
            "Altura", "altura", "Height",
            "Peso", "peso", "Weight",
            "Nacionalidad", "nacionalidad", "Nationality",
            "Pie", "pie", "Foot",
            "Fecha de nacimiento", "Born",
            "Minutos", "minutos", "Minutes",
            "Tarjetas amarillas", "Amarillas",
            "Tarjetas rojas", "Rojas",
            "Asistencias", "asistencias", "Assists",
            "Valor de mercado", "Market value"
        ]

        for campo in campos_buscar:
            if campo in texto_completo:
                print(f"      ✅ Encontrado: '{campo}'")
                datos_ficha["datos_encontrados"][campo] = True
            else:
                datos_ficha["datos_encontrados"][campo] = False

        # 4. Guardar HTML completo para análisis manual (primeros 5000 caracteres)
        datos_ficha["html_preview"] = content[:5000]

        return datos_ficha

    except Exception as e:
        print(f"   ❌ Error explorando ficha: {str(e)[:100]}")
        return {"nombre": nombre, "error": str(e)}


async def main():
    print("\n" + "="*70)
    print("🔬 EXPLORACIÓN: BeSoccer - Fichas Individuales de Jugadores")
    print("="*70 + "\n")

    print(f"🎯 Equipo: {EQUIPO_NOMBRE}")
    print(f"📝 Analizaremos {LIMITE_JUGADORES} jugadores para comparar datos\n")

    async with async_playwright() as p:
        print("🦊 Lanzando Firefox...")
        browser = await p.firefox.launch(headless=True, timeout=60000)

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-ES'
        )

        page = await context.new_page()

        # PASO 1: Extraer datos de tabla de plantilla
        print(f"\n📡 Navegando a plantilla del equipo...")
        await page.goto(EQUIPO_URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)

        jugadores_tabla = await extraer_datos_tabla_plantilla(page)

        if not jugadores_tabla:
            print("❌ No se pudieron extraer jugadores de la tabla")
            await browser.close()
            return

        # PASO 2: Explorar fichas individuales de los primeros N jugadores
        print(f"\n{'='*70}")
        print(f"🔍 EXPLORANDO FICHAS INDIVIDUALES")
        print(f"{'='*70}")

        resultados = {
            "equipo": EQUIPO_NOMBRE,
            "url_equipo": EQUIPO_URL,
            "fecha_exploracion": datetime.now().isoformat(),
            "jugadores_tabla": jugadores_tabla[:LIMITE_JUGADORES],
            "fichas_individuales": []
        }

        for idx, jugador in enumerate(jugadores_tabla[:LIMITE_JUGADORES], 1):
            if not jugador.get('url_perfil'):
                print(f"\n⚠️  Jugador {idx}: {jugador['nombre']} - No tiene URL de perfil")
                continue

            await asyncio.sleep(3)  # Delay entre jugadores

            ficha = await extraer_datos_ficha_individual(
                page,
                jugador['url_perfil'],
                jugador['nombre']
            )

            resultados["fichas_individuales"].append(ficha)

        await browser.close()
        print("\n✅ Firefox cerrado")

        # PASO 3: ANÁLISIS Y RESUMEN
        print(f"\n{'='*70}")
        print(f"📊 RESUMEN DE HALLAZGOS")
        print(f"{'='*70}\n")

        print(f"📋 DATOS DISPONIBLES EN TABLA DE PLANTILLA:")
        print(f"   • Dorsal")
        print(f"   • Nombre")
        print(f"   • Partidos jugados")
        print(f"   • Goles")
        print(f"   • Edad")
        print(f"   • URL de perfil individual\n")

        print(f"🔍 DATOS ENCONTRADOS EN FICHAS INDIVIDUALES:\n")

        # Consolidar campos encontrados
        campos_consolidados = {}
        for ficha in resultados["fichas_individuales"]:
            if "datos_encontrados" in ficha:
                for campo, encontrado in ficha["datos_encontrados"].items():
                    if campo not in campos_consolidados:
                        campos_consolidados[campo] = 0
                    if encontrado:
                        campos_consolidados[campo] += 1

        if campos_consolidados:
            print("   Campos encontrados (frecuencia):")
            for campo, count in sorted(campos_consolidados.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    porcentaje = (count / len(resultados["fichas_individuales"])) * 100
                    print(f"   ✅ {campo}: {count}/{len(resultados['fichas_individuales'])} jugadores ({porcentaje:.0f}%)")
        else:
            print("   ⚠️  No se encontraron campos adicionales en las fichas individuales")

        # Guardar resultados completos en JSON
        output_file = f"research/data_samples/analisis_ligas/exploracion_besoccer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultados detallados guardados en:")
        print(f"   {output_file}")

        print(f"\n{'='*70}")
        print(f"💡 CONCLUSIÓN")
        print(f"{'='*70}\n")

        print("Revisa el JSON generado para:")
        print("1. Ver estructura HTML de las fichas individuales")
        print("2. Identificar qué datos adicionales están disponibles")
        print("3. Decidir si vale la pena scrapear fichas individuales")
        print("4. Diseñar estrategia de extracción si hay datos valiosos\n")


if __name__ == "__main__":
    asyncio.run(main())
