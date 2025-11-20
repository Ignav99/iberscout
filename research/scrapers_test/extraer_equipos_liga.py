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

# URL del grupo de 3ª RFEF (Grupo 1 - Galicia)
GRUPO_URL = "https://es.besoccer.com/competicion/clasificacion/tercera_division_rfef/2024/grupo1"

OUTPUT_FILE = Path("research/data_samples/analisis_ligas/equipos_3rfef_grupo1.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


async def extraer_equipos():
    """Extrae la lista de equipos del grupo"""
    print("\n" + "="*70)
    print("🔍 EXTRAYENDO EQUIPOS DE 3ª RFEF - GRUPO 1")
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

        # Buscar la tabla de clasificación
        tabla = soup.find('table', class_='table-striped') or soup.find('table')

        if not tabla:
            print("❌ No se encontró tabla de clasificación")
            await browser.close()
            return []

        print("✅ Tabla encontrada")

        equipos = []
        filas = tabla.find_all('tr')

        for fila in filas:
            # Buscar enlace del equipo
            enlace = fila.find('a', href=lambda x: x and '/equipo/' in x)

            if enlace:
                nombre_equipo = enlace.get_text(strip=True)
                url_equipo = enlace.get('href')

                # Construir URL completa
                if url_equipo.startswith('/'):
                    url_equipo = f"https://es.besoccer.com{url_equipo}"

                # Convertir URL de info a URL de plantilla
                # Ej: /equipo/info/xxx → /equipo/plantilla/xxx
                url_plantilla = url_equipo.replace('/info/', '/plantilla/')

                equipos.append({
                    "nombre": nombre_equipo,
                    "url": url_plantilla
                })

        await browser.close()

        print(f"\n✅ Equipos extraídos: {len(equipos)}")

        # Mostrar equipos encontrados
        print("\n📋 EQUIPOS ENCONTRADOS:")
        for i, equipo in enumerate(equipos, 1):
            print(f"   {i:2d}. {equipo['nombre']}")

        # Guardar en JSON
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(equipos, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Lista guardada en: {OUTPUT_FILE}")

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
