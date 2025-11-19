"""
==========================================
IBERSCOUT - SCRAPER CON PLAYWRIGHT + FIREFOX
==========================================
Usando Firefox porque Chromium falla en Mac
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("research/data_samples/analisis_ligas")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EQUIPOS_PRUEBA = {
    "Segunda División": {
        "nombre": "CD Mirandés",
        "url": "https://es.besoccer.com/equipo/plantilla/mirandes"
    }
}


async def extraer_con_firefox(url, equipo_nombre):
    """
    Extrae jugadores usando Playwright con Firefox
    """
    print(f"\n{'='*70}")
    print(f"🔍 {equipo_nombre}")
    print(f"🌐 {url}")
    print(f"{'='*70}\n")
    
    async with async_playwright() as p:
        try:
            print("🦊 Lanzando Firefox...")
            
            # USAR FIREFOX en lugar de Chromium
            browser = await p.firefox.launch(
                headless=False,  # Ver qué pasa
                timeout=60000
            )
            
            print("✅ Firefox lanzado")
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='es-ES'
            )
            
            page = await context.new_page()
            
            print("📡 Navegando a BeSoccer...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            print("⏳ Esperando que cargue el contenido...")
            await page.wait_for_timeout(5000)  # 5 segundos
            
            # Verificar si hay Cloudflare Challenge
            content = await page.content()
            
            if "challenge" in content.lower() or "checking your browser" in content.lower():
                print("⚠️  Detectado Cloudflare Challenge")
                print("⏳ Esperando 10 segundos más...")
                await page.wait_for_timeout(10000)
                content = await page.content()
            
            # Guardar HTML
            html_path = OUTPUT_DIR / "besoccer_firefox_test.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"💾 HTML guardado: {html_path.name}")
            
            # Parsear
            soup = BeautifulSoup(content, 'html.parser')
            
            # Buscar tablas
            tablas = soup.find_all('table')
            print(f"📊 Tablas encontradas: {len(tablas)}")
            
            if tablas:
                print("✅ ¡Contenido cargado correctamente!")
                
                # Buscar palabras clave
                texto = soup.get_text()
                posiciones_encontradas = []
                for pos in ['Portero', 'Defensa', 'Centrocampista', 'Delantero']:
                    if pos in texto:
                        posiciones_encontradas.append(pos)
                
                if posiciones_encontradas:
                    print(f"✅ Posiciones detectadas: {', '.join(posiciones_encontradas)}")
                else:
                    print("⚠️  No se detectaron posiciones en el texto")
                
                # Analizar primera tabla
                tabla = tablas[0]
                filas = tabla.find_all('tr')
                print(f"📊 Filas en tabla: {len(filas)}")
                
                # Mostrar primeras 5 filas
                print("\n📋 PRIMERAS 5 FILAS:")
                for i, fila in enumerate(filas[:5], 1):
                    texto_fila = fila.get_text(strip=True)
                    print(f"   {i}. {texto_fila[:100]}")
                
            else:
                print("❌ No se encontraron tablas")
                print("💡 El contenido dinámico no se cargó")
                
                # Mostrar parte del HTML
                print(f"\n📄 Primeros 500 caracteres del HTML:")
                print(content[:500])
            
            await browser.close()
            print("\n✅ Prueba completada")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            try:
                await browser.close()
            except:
                pass


async def main():
    print("\n" + "🦊"*35)
    print("   IBERSCOUT - TEST CON FIREFOX")
    print("🦊"*35 + "\n")
    
    print("🎯 Objetivo: Verificar si Firefox puede acceder a BeSoccer")
    print("⚠️  Se abrirá una ventana de Firefox\n")
    
    input("Presiona ENTER para comenzar...")
    
    for liga, equipo_info in EQUIPOS_PRUEBA.items():
        await extraer_con_firefox(equipo_info['url'], equipo_info['nombre'])


if __name__ == "__main__":
    # Verificar que Firefox está instalado
    print("\n🔍 Verificando instalación de Firefox...")
    print("💡 Si falla, ejecuta: playwright install firefox\n")
    
    asyncio.run(main())