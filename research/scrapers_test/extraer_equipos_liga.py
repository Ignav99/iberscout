"""
==========================================
AUXILIAR: Extraer lista de equipos de BeSoccer
==========================================
Usa Playwright+Firefox para extraer todos los equipos de un grupo de 3ª RFEF
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from pathlib import Path
import re

# URL del grupo de 3ª RFEF (Grupo 1 - Galicia)
# Cambiar el número de grupo según necesidad (grupo1, grupo2, ..., grupo18)
GRUPO_URL = "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/2024/grupo1"
GRUPO_NOMBRE = "Grupo 1 - Galicia"

OUTPUT_FILE = Path("research/data_samples/analisis_ligas/equipos_3rfef_grupo1.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def convertir_a_url_plantilla(url):
    """Convierte cualquier URL de equipo a formato /equipo/plantilla/xxx"""
    # Extraer el slug del equipo de cualquier URL
    # Ejemplos:
    # /equipo/info/sd-compostela → sd-compostela
    # /equipo/plantilla/arosa → arosa
    # /equipo/sd-compostela → sd-compostela

    match = re.search(r'/equipo/(?:info/|plantilla/)?([^/]+)', url)
    if match:
        slug = match.group(1)
        return f"https://es.besoccer.com/equipo/plantilla/{slug}"
    return url


async def extraer_equipos():
    """Extrae la lista de equipos del grupo"""
    print("\n" + "="*70)
    print(f"🔍 EXTRAYENDO EQUIPOS DE 3ª RFEF - {GRUPO_NOMBRE}")
    print("="*70 + "\n")

    async with async_playwright() as p:
        print("🦊 Lanzando Firefox...")
        browser = await p.firefox.launch(headless=True, timeout=60000)

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-ES'
        )

        page = await context.new_page()

        print(f"📡 Navegando a {GRUPO_URL}...")
        await page.goto(GRUPO_URL, wait_until="networkidle", timeout=60000)

        print("⏳ Esperando contenido...")
        await page.wait_for_timeout(3000)

        # Obtener HTML
        content = await page.content()

        # Parsear con BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Buscar SOLO en la tabla de clasificación (NO en banners/widgets)
        tabla = soup.find('table', class_='table-striped') or soup.find('table')

        if not tabla:
            print("❌ No se encontró tabla de clasificación")
            await browser.close()
            return []

        # Extraer SOLO enlaces de equipos de la tabla
        enlaces_equipos = tabla.find_all('a', href=re.compile(r'/equipo/'))

        if not enlaces_equipos:
            print("❌ No se encontraron enlaces de equipos en la tabla")
            await browser.close()
            return []

        print(f"✅ Enlaces encontrados en tabla: {len(enlaces_equipos)}")

        equipos = []
        equipos_vistos = set()  # Para evitar duplicados

        for enlace in enlaces_equipos:
            nombre_equipo = enlace.get_text(strip=True)
            url_equipo = enlace.get('href')

            # Saltar si no tiene nombre o URL
            if not nombre_equipo or not url_equipo:
                continue

            # Saltar si ya procesamos este equipo
            if nombre_equipo in equipos_vistos:
                continue

            # Construir URL completa
            if url_equipo.startswith('/'):
                url_equipo = f"https://es.besoccer.com{url_equipo}"

            # Convertir a URL de plantilla
            url_plantilla = convertir_a_url_plantilla(url_equipo)

            equipos.append({
                "nombre": nombre_equipo,
                "url": url_plantilla
            })

            equipos_vistos.add(nombre_equipo)

        await browser.close()

        print(f"\n✅ Equipos únicos extraídos: {len(equipos)}")

        # Mostrar equipos encontrados
        print("\n📋 EQUIPOS ENCONTRADOS:")
        for i, equipo in enumerate(equipos, 1):
            print(f"   {i:2d}. {equipo['nombre']}")
            print(f"       URL: {equipo['url']}")

        # Guardar en JSON
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(equipos, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Lista guardada en: {OUTPUT_FILE}")

        # Validación
        print(f"\n🔍 VALIDACIÓN:")
        print(f"   • Total equipos: {len(equipos)}")
        print(f"   • Todas las URLs apuntan a /plantilla/: ", end="")
        todas_plantilla = all('/plantilla/' in eq['url'] for eq in equipos)
        print("✅" if todas_plantilla else "❌")
        print(f"   • Todas las URLs son únicas: ", end="")
        urls_unicas = len(set(eq['url'] for eq in equipos)) == len(equipos)
        print("✅" if urls_unicas else "❌")

        return equipos


if __name__ == "__main__":
    equipos = asyncio.run(extraer_equipos())

    if equipos:
        print(f"\n🎉 ¡Listo! {len(equipos)} equipos disponibles para scraping masivo")
        print(f"\n📝 Siguiente paso:")
        print(f"   Revisar: {OUTPUT_FILE}")
        print(f"   Ejecutar: python research/scrapers_test/06_extraccion_liga_completa.py")
    else:
        print(f"\n❌ No se pudieron extraer equipos")
