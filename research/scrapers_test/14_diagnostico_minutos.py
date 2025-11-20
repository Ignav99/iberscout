"""
==========================================
DIAGNÓSTICO: Extracción de minutos de BeSoccer
==========================================
Script para depurar por qué no se extraen los minutos
Prueba con 1 jugador específico y muestra TODO el proceso
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

# URL de prueba (Canedo - Bergantiños)
URL_JUGADOR = "https://es.besoccer.com/jugador/canedo-164269"
NOMBRE_JUGADOR = "Canedo"


async def diagnostico_completo(page, url):
    """Diagnóstico detallado de extracción"""
    print("\n" + "="*70)
    print(f"🔬 DIAGNÓSTICO: {NOMBRE_JUGADOR}")
    print("="*70 + "\n")

    print(f"📡 URL: {url}\n")

    try:
        print("⏱️  Navegando a la página...")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        print("✅ Página cargada (networkidle)")

        # Esperar más tiempo para JavaScript
        print("⏳ Esperando 5 segundos para JavaScript...")
        await page.wait_for_timeout(5000)
        print("✅ Espera completada\n")

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        print("="*70)
        print("📊 ANÁLISIS DE TABLAS")
        print("="*70 + "\n")

        # Buscar TODAS las tablas
        tablas = soup.find_all('table')
        print(f"Total tablas encontradas: {len(tablas)}\n")

        for idx, tabla in enumerate(tablas, 1):
            print(f"--- TABLA {idx} ---")

            # Headers
            headers = tabla.find_all('th')
            if headers:
                headers_text = [th.get_text(strip=True) for th in headers]
                print(f"Headers ({len(headers_text)}): {headers_text}")
            else:
                print("Headers: (sin <th>, buscando primera fila)")
                primera_fila = tabla.find('tr')
                if primera_fila:
                    celdas = primera_fila.find_all('td')
                    headers_text = [td.get_text(strip=True) for td in celdas]
                    print(f"Primera fila ({len(headers_text)}): {headers_text}")

            # Buscar "MIN" en cualquier forma
            headers_lower = [h.lower() for h in headers_text] if headers_text else []

            tiene_min = any('min' in h for h in headers_lower)
            if tiene_min:
                print("✅ CONTIENE 'MIN'")

                # Buscar índice exacto
                idx_min = None
                for i, h in enumerate(headers_lower):
                    if 'min' in h:
                        idx_min = i
                        print(f"   Índice MIN: {i} (Header: '{headers_text[i]}')")
                        break

                # Extraer primera fila de datos
                filas = tabla.find_all('tr')
                if len(filas) > 1:
                    fila_datos = filas[1]
                    celdas = fila_datos.find_all('td')
                    print(f"   Celdas en fila de datos: {len(celdas)}")

                    if len(celdas) > idx_min:
                        valor_min = celdas[idx_min].get_text(strip=True)
                        print(f"   ⭐ VALOR MINUTOS: '{valor_min}'")

                        # Limpiar y convertir
                        valor_limpio = valor_min.replace('.', '').replace(',', '')
                        if valor_limpio.isdigit():
                            print(f"   ✅ Minutos extraídos: {int(valor_limpio)}")
                        else:
                            print(f"   ⚠️  No es numérico: '{valor_limpio}'")

            print()

        # BUSCAR PIE DOMINANTE Y NACIONALIDAD EN TEXTO
        print("="*70)
        print("📝 BÚSQUEDA EN TEXTO COMPLETO")
        print("="*70 + "\n")

        texto_completo = soup.get_text()

        # Pie dominante
        print("🔍 Buscando 'Pie:'...")
        if 'Pie:' in texto_completo or 'pie:' in texto_completo:
            print("   ✅ Encontrado 'Pie:' en página")

            # Extraer contexto
            idx = texto_completo.find('Pie:')
            if idx == -1:
                idx = texto_completo.find('pie:')

            contexto = texto_completo[max(0, idx-20):idx+50]
            print(f"   Contexto: ...{contexto}...")

            # Regex
            match = re.search(r'[Pp]ie:\s*(Derecho|Izquierdo|Ambidiestro)', texto_completo)
            if match:
                print(f"   ⭐ PIE DOMINANTE: {match.group(1)}")
            else:
                print("   ⚠️  No se pudo extraer con regex")
        else:
            print("   ❌ NO encontrado 'Pie:' en página")

        # Nacionalidad
        print("\n🔍 Buscando 'Nacionalidad:'...")
        if 'nacionalidad' in texto_completo.lower():
            print("   ✅ Encontrado 'Nacionalidad' en página")

            # Extraer contexto
            idx = texto_completo.lower().find('nacionalidad')
            contexto = texto_completo[idx:idx+100]
            print(f"   Contexto: {contexto[:80]}...")

            # Regex
            match = re.search(r'[Nn]acionalidad:\s*([A-Za-záéíóúñÑ]+)', texto_completo)
            if match:
                print(f"   ⭐ NACIONALIDAD: {match.group(1)}")
            else:
                print("   ⚠️  No se pudo extraer con regex")
        else:
            print("   ❌ NO encontrado 'Nacionalidad' en página")

        # GUARDAR HTML PARA INSPECCIÓN MANUAL
        print("\n" + "="*70)
        print("💾 GUARDANDO HTML PARA INSPECCIÓN")
        print("="*70 + "\n")

        with open("research/data_samples/analisis_ligas/debug_ficha.html", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ HTML guardado en: research/data_samples/analisis_ligas/debug_ficha.html")
        print("   Abre este archivo para inspeccionar manualmente\n")

    except Exception as e:
        print(f"\n❌ ERROR DURANTE DIAGNÓSTICO:")
        print(f"   {str(e)}\n")


async def main():
    print("\n🔬 SCRIPT DE DIAGNÓSTICO - EXTRACCIÓN DE MINUTOS")
    print("="*70)

    async with async_playwright() as p:
        print("\n🦊 Lanzando Firefox...")
        browser = await p.firefox.launch(headless=False, timeout=60000)  # headless=False para ver

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-ES'
        )

        page = await context.new_page()

        await diagnostico_completo(page, URL_JUGADOR)

        print("\n⏸️  Presiona ENTER para cerrar el navegador...")
        input()

        await browser.close()
        print("✅ Diagnóstico completado\n")


if __name__ == "__main__":
    asyncio.run(main())
