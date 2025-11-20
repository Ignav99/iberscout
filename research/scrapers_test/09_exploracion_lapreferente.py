"""
==========================================
SPRINT 5: EXPLORACIÓN - LaPreferente.com
==========================================
Objetivo: Investigar QUÉ datos de 3ª RFEF tiene LaPreferente
Comparar con BeSoccer para decidir si usamos múltiples fuentes
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime

# CONFIGURACIÓN
# LaPreferente tiene URLs por grupo, ejemplo:
# https://www.lapreferente.com/C14947-13/tercera-rfef-grupo-1/goleadores.html
# https://www.lapreferente.com/C14947-1/tercera-rfef-grupo-1/ranking.html (clasificación)

GRUPO_URL = "https://www.lapreferente.com/C14947-1/tercera-rfef-grupo-1/ranking.html"
GRUPO_NOMBRE = "3ª RFEF - Grupo 1 (Galicia)"


async def explorar_pagina_clasificacion(page):
    """Explora la página de clasificación para entender estructura"""
    print("📊 Explorando página de clasificación...")

    try:
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Buscar tablas
        tablas = soup.find_all('table')
        print(f"   Tablas encontradas: {len(tablas)}")

        # Buscar enlaces a equipos
        enlaces_equipos = soup.find_all('a', href=lambda x: x and 'equipo' in x.lower())
        print(f"   Enlaces a equipos encontrados: {len(enlaces_equipos)}")

        if enlaces_equipos:
            print(f"   Ejemplo URL equipo: {enlaces_equipos[0].get('href')}")

        return {
            "num_tablas": len(tablas),
            "num_enlaces_equipos": len(enlaces_equipos),
            "ejemplo_url_equipo": enlaces_equipos[0].get('href') if enlaces_equipos else None
        }

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return {"error": str(e)}


async def explorar_pagina_goleadores(page):
    """Explora la página de goleadores/estadísticas"""
    print("\n⚽ Explorando página de goleadores...")

    try:
        # Cambiar a página de goleadores
        url_goleadores = GRUPO_URL.replace("/ranking.html", "/goleadores.html")
        print(f"   URL: {url_goleadores}")

        await page.goto(url_goleadores, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Buscar tabla de goleadores
        tablas = soup.find_all('table')
        print(f"   Tablas encontradas: {len(tablas)}")

        if not tablas:
            print("   ⚠️  No se encontraron tablas")
            return {"error": "No se encontraron tablas"}

        # Analizar primera tabla (probablemente goleadores)
        tabla = tablas[0]
        headers = [th.get_text(strip=True) for th in tabla.find_all('th')]
        print(f"   📋 Headers de tabla: {headers}")

        # Extraer primera fila como ejemplo
        primera_fila = tabla.find('tr')
        if primera_fila and primera_fila.find_all('td'):
            celdas = [td.get_text(strip=True) for td in primera_fila.find_all('td')]
            print(f"   📝 Ejemplo datos: {celdas}")

        # Buscar enlaces a fichas de jugadores
        enlaces_jugadores = tabla.find_all('a', href=lambda x: x and 'jugador' in x.lower())
        print(f"   👤 Enlaces a jugadores encontrados: {len(enlaces_jugadores)}")

        if enlaces_jugadores:
            print(f"   Ejemplo URL jugador: {enlaces_jugadores[0].get('href')}")

        return {
            "url": url_goleadores,
            "num_tablas": len(tablas),
            "headers": headers,
            "num_enlaces_jugadores": len(enlaces_jugadores),
            "ejemplo_url_jugador": enlaces_jugadores[0].get('href') if enlaces_jugadores else None
        }

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return {"error": str(e)}


async def explorar_otras_secciones(page):
    """Explora otras secciones disponibles (tarjetas, etc.)"""
    print("\n🔍 Explorando otras secciones...")

    secciones = [
        ("tarjetas", "Tarjetas amarillas/rojas"),
        ("estadisticas", "Estadísticas generales"),
        ("topJugadores", "Top jugadores")
    ]

    resultados = {}

    for seccion, nombre in secciones:
        try:
            url_seccion = GRUPO_URL.replace("/ranking.html", f"/{seccion}.html")
            print(f"\n   📄 {nombre}")
            print(f"      URL: {url_seccion}")

            await page.goto(url_seccion, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Verificar si la página existe (no es 404)
            if "404" in soup.get_text() or "no encontrada" in soup.get_text().lower():
                print(f"      ❌ Página no disponible")
                resultados[seccion] = {"disponible": False}
                continue

            # Buscar tablas
            tablas = soup.find_all('table')

            if tablas:
                headers = [th.get_text(strip=True) for th in tablas[0].find_all('th')]
                print(f"      ✅ Disponible - Headers: {headers}")
                resultados[seccion] = {
                    "disponible": True,
                    "headers": headers,
                    "num_tablas": len(tablas)
                }
            else:
                print(f"      ⚠️  Sin tablas")
                resultados[seccion] = {"disponible": False}

        except Exception as e:
            print(f"      ❌ Error: {str(e)[:50]}")
            resultados[seccion] = {"error": str(e)}

    return resultados


async def main():
    print("\n" + "="*70)
    print("🔬 EXPLORACIÓN: LaPreferente.com - 3ª RFEF")
    print("="*70 + "\n")

    print(f"🎯 Grupo: {GRUPO_NOMBRE}")
    print(f"📝 Investigaremos qué datos están disponibles\n")

    async with async_playwright() as p:
        print("🦊 Lanzando Firefox...")
        browser = await p.firefox.launch(headless=True, timeout=60000)

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-ES'
        )

        page = await context.new_page()

        resultados = {
            "fuente": "LaPreferente.com",
            "grupo": GRUPO_NOMBRE,
            "url_base": GRUPO_URL,
            "fecha_exploracion": datetime.now().isoformat(),
            "hallazgos": {}
        }

        # PASO 1: Explorar clasificación
        print(f"\n📡 Navegando a página de clasificación...")
        try:
            await page.goto(GRUPO_URL, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            resultados["hallazgos"]["clasificacion"] = await explorar_pagina_clasificacion(page)
        except Exception as e:
            print(f"❌ Error accediendo a clasificación: {str(e)[:100]}")
            resultados["hallazgos"]["clasificacion"] = {"error": str(e)}

        await asyncio.sleep(3)

        # PASO 2: Explorar goleadores
        try:
            resultados["hallazgos"]["goleadores"] = await explorar_pagina_goleadores(page)
        except Exception as e:
            print(f"❌ Error accediendo a goleadores: {str(e)[:100]}")
            resultados["hallazgos"]["goleadores"] = {"error": str(e)}

        await asyncio.sleep(3)

        # PASO 3: Explorar otras secciones
        try:
            resultados["hallazgos"]["otras_secciones"] = await explorar_otras_secciones(page)
        except Exception as e:
            print(f"❌ Error explorando otras secciones: {str(e)[:100]}")
            resultados["hallazgos"]["otras_secciones"] = {"error": str(e)}

        await browser.close()
        print("\n✅ Firefox cerrado")

        # RESUMEN
        print(f"\n{'='*70}")
        print(f"📊 RESUMEN DE HALLAZGOS - LaPreferente")
        print(f"{'='*70}\n")

        print("✅ Secciones disponibles:")
        if resultados["hallazgos"].get("clasificacion", {}).get("num_tablas", 0) > 0:
            print("   • Clasificación (tabla de posiciones)")

        if resultados["hallazgos"].get("goleadores", {}).get("num_tablas", 0) > 0:
            print("   • Goleadores")
            headers = resultados["hallazgos"]["goleadores"].get("headers", [])
            if headers:
                print(f"     Campos: {', '.join(headers)}")

        otras = resultados["hallazgos"].get("otras_secciones", {})
        for seccion, datos in otras.items():
            if datos.get("disponible"):
                print(f"   • {seccion.capitalize()}")
                if "headers" in datos:
                    print(f"     Campos: {', '.join(datos['headers'])}")

        # Guardar resultados
        output_file = f"research/data_samples/analisis_ligas/exploracion_lapreferente_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultados detallados guardados en:")
        print(f"   {output_file}")

        print(f"\n{'='*70}")
        print(f"💡 CONCLUSIÓN")
        print(f"{'='*70}\n")

        print("Revisa el JSON generado para:")
        print("1. Ver qué secciones están disponibles")
        print("2. Identificar campos/columnas de cada tabla")
        print("3. Comparar con BeSoccer")
        print("4. Decidir si aporta datos adicionales valiosos\n")


if __name__ == "__main__":
    asyncio.run(main())
