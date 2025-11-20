"""
==========================================
SPRINT 5: EXPLORACIÓN - FutbolMe
==========================================
Objetivo: Investigar QUÉ datos de 3ª RFEF tiene FutbolMe
Comparar con BeSoccer y LaPreferente
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime

# CONFIGURACIÓN
# FutbolMe URLs ejemplo:
# https://futbolme.com/resultados-directo/torneo/tercera-division-rfef-grupo-3/3063/equipos
GRUPO_URL = "https://futbolme.com/resultados-directo/torneo/tercera-division-rfef-grupo-1/3061/"
GRUPO_NOMBRE = "3ª RFEF - Grupo 1 (Galicia)"


async def explorar_pagina_principal(page):
    """Explora la página principal del grupo"""
    print("📊 Explorando página principal del grupo...")

    try:
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Buscar secciones/tabs disponibles
        tabs = soup.find_all(['a', 'button'], class_=lambda x: x and ('tab' in x.lower() or 'menu' in x.lower()))
        print(f"   Tabs/secciones encontradas: {len(tabs)}")

        if tabs:
            for tab in tabs[:10]:  # Primeros 10
                texto = tab.get_text(strip=True)
                href = tab.get('href', '')
                print(f"      • {texto} → {href}")

        # Buscar tablas
        tablas = soup.find_all('table')
        print(f"   Tablas encontradas: {len(tablas)}")

        # Buscar enlaces a equipos
        enlaces_equipos = soup.find_all('a', href=lambda x: x and 'equipo' in x.lower())
        print(f"   Enlaces a equipos: {len(enlaces_equipos)}")

        return {
            "num_tabs": len(tabs),
            "num_tablas": len(tablas),
            "num_enlaces_equipos": len(enlaces_equipos)
        }

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return {"error": str(e)}


async def explorar_seccion_equipos(page):
    """Explora la sección de equipos"""
    print("\n⚽ Explorando sección de equipos...")

    try:
        url_equipos = GRUPO_URL.rstrip('/') + "/equipos"
        print(f"   URL: {url_equipos}")

        await page.goto(url_equipos, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Buscar lista de equipos
        enlaces_equipos = soup.find_all('a', href=lambda x: x and 'equipo' in x)
        print(f"   Equipos encontrados: {len(enlaces_equipos)}")

        if enlaces_equipos:
            ejemplo_url = enlaces_equipos[0].get('href')
            print(f"   Ejemplo URL equipo: {ejemplo_url}")

            # Intentar explorar un equipo
            if not ejemplo_url.startswith('http'):
                ejemplo_url = "https://futbolme.com" + ejemplo_url

            print(f"\n   🔍 Explorando equipo de ejemplo...")
            await page.goto(ejemplo_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            content_equipo = await page.content()
            soup_equipo = BeautifulSoup(content_equipo, 'html.parser')

            # Buscar plantilla
            tablas_equipo = soup_equipo.find_all('table')
            print(f"      Tablas en página de equipo: {len(tablas_equipo)}")

            if tablas_equipo:
                headers = [th.get_text(strip=True) for th in tablas_equipo[0].find_all('th')]
                print(f"      📋 Headers: {headers}")

            return {
                "url": url_equipos,
                "num_equipos": len(enlaces_equipos),
                "ejemplo_url_equipo": ejemplo_url,
                "num_tablas_equipo": len(tablas_equipo),
                "headers_equipo": headers if tablas_equipo else []
            }

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return {"error": str(e)}


async def explorar_seccion_estadisticas(page):
    """Explora la sección de estadísticas/goleadores"""
    print("\n📊 Explorando sección de estadísticas...")

    secciones = [
        ("goleadores", "Tabla de goleadores"),
        ("estadisticas", "Estadísticas generales"),
        ("clasificacion", "Clasificación")
    ]

    resultados = {}

    for seccion, nombre in secciones:
        try:
            url_seccion = GRUPO_URL.rstrip('/') + f"/{seccion}"
            print(f"\n   📄 {nombre}")
            print(f"      URL: {url_seccion}")

            await page.goto(url_seccion, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Buscar tablas
            tablas = soup.find_all('table')

            if tablas:
                headers = [th.get_text(strip=True) for th in tablas[0].find_all('th')]
                print(f"      ✅ Disponible - Headers: {headers}")

                # Buscar enlaces a jugadores
                enlaces_jugadores = tablas[0].find_all('a', href=lambda x: x and 'jugador' in x)
                print(f"      👤 Enlaces a jugadores: {len(enlaces_jugadores)}")

                resultados[seccion] = {
                    "disponible": True,
                    "headers": headers,
                    "num_tablas": len(tablas),
                    "num_enlaces_jugadores": len(enlaces_jugadores)
                }
            else:
                print(f"      ⚠️  Sin tablas (puede no estar disponible)")
                resultados[seccion] = {"disponible": False}

        except Exception as e:
            print(f"      ❌ Error: {str(e)[:50]}")
            resultados[seccion] = {"error": str(e)}

        await asyncio.sleep(2)

    return resultados


async def main():
    print("\n" + "="*70)
    print("🔬 EXPLORACIÓN: FutbolMe - 3ª RFEF")
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
            "fuente": "FutbolMe",
            "grupo": GRUPO_NOMBRE,
            "url_base": GRUPO_URL,
            "fecha_exploracion": datetime.now().isoformat(),
            "hallazgos": {}
        }

        # PASO 1: Explorar página principal
        print(f"\n📡 Navegando a página principal del grupo...")
        try:
            await page.goto(GRUPO_URL, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            resultados["hallazgos"]["pagina_principal"] = await explorar_pagina_principal(page)
        except Exception as e:
            print(f"❌ Error accediendo a página principal: {str(e)[:100]}")
            resultados["hallazgos"]["pagina_principal"] = {"error": str(e)}

        await asyncio.sleep(3)

        # PASO 2: Explorar equipos
        try:
            resultados["hallazgos"]["equipos"] = await explorar_seccion_equipos(page)
        except Exception as e:
            print(f"❌ Error explorando equipos: {str(e)[:100]}")
            resultados["hallazgos"]["equipos"] = {"error": str(e)}

        await asyncio.sleep(3)

        # PASO 3: Explorar estadísticas
        try:
            resultados["hallazgos"]["estadisticas"] = await explorar_seccion_estadisticas(page)
        except Exception as e:
            print(f"❌ Error explorando estadísticas: {str(e)[:100]}")
            resultados["hallazgos"]["estadisticas"] = {"error": str(e)}

        await browser.close()
        print("\n✅ Firefox cerrado")

        # RESUMEN
        print(f"\n{'='*70}")
        print(f"📊 RESUMEN DE HALLAZGOS - FutbolMe")
        print(f"{'='*70}\n")

        print("✅ Secciones disponibles:")

        equipos = resultados["hallazgos"].get("equipos", {})
        if equipos.get("num_equipos", 0) > 0:
            print(f"   • Equipos ({equipos['num_equipos']} equipos)")
            if equipos.get("headers_equipo"):
                print(f"     Campos plantilla: {', '.join(equipos['headers_equipo'])}")

        estadisticas = resultados["hallazgos"].get("estadisticas", {})
        for seccion, datos in estadisticas.items():
            if datos.get("disponible"):
                print(f"   • {seccion.capitalize()}")
                if "headers" in datos:
                    print(f"     Campos: {', '.join(datos['headers'])}")
                if "num_enlaces_jugadores" in datos and datos["num_enlaces_jugadores"] > 0:
                    print(f"     Enlaces a jugadores: {datos['num_enlaces_jugadores']}")

        # Guardar resultados
        output_file = f"research/data_samples/analisis_ligas/exploracion_futbolme_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        print("3. Comparar con BeSoccer y LaPreferente")
        print("4. Decidir la fuente óptima para 3ª RFEF\n")


if __name__ == "__main__":
    asyncio.run(main())
