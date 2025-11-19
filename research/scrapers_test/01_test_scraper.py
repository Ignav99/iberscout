"""
==========================================
IBERSCOUT - SCRAPER DE PRUEBA INICIAL
==========================================
Script básico para verificar que Playwright funciona correctamente
Objetivo: Hacer una petición simple a BeSoccer y extraer información básica
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
from config.settings import ScrapingConfig, PathsConfig


async def test_scraper_besoccer():
    """
    Prueba básica de scraping en BeSoccer
    Objetivo: Extraer el título y verificar que no nos bloquean
    """
    
    print("\n" + "="*60)
    print("🕷️  SCRAPER DE PRUEBA - BESOCCER")
    print("="*60 + "\n")
    
    # Configuración
    url = "https://www.besoccer.com"
    
    async with async_playwright() as p:
        # Lanzar navegador (chromium)
        print("🌐 Lanzando navegador Chromium...")
        browser = await p.chromium.launch(
            headless=False,  # Cambia a True para modo invisible
            slow_mo=1000     # Ralentizar acciones para debugging
        )
        
        # Crear contexto (como una sesión de navegador)
        context = await browser.new_context(
            user_agent=ScrapingConfig.USER_AGENT,
            viewport={"width": 1920, "height": 1080}
        )
        
        # Crear página
        page = await context.new_page()
        
        try:
            print(f"📍 Navegando a: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Esperar un poco para que cargue contenido dinámico
            await page.wait_for_timeout(2000)
            
            # Extraer título de la página
            title = await page.title()
            print(f"✅ Título de la página: {title}\n")
            
            # Extraer el HTML de la sección de resultados (ejemplo)
            # Nota: Esto es solo para verificar, no extraemos datos aún
            content = await page.content()
            print(f"📄 HTML capturado: {len(content)} caracteres\n")
            
            # Tomar screenshot (prueba)
            screenshot_path = PathsConfig.RESEARCH_DIR / "data_samples" / f"besoccer_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"📸 Screenshot guardado: {screenshot_path}\n")
            
            # Guardar información básica
            result = {
                "url": url,
                "title": title,
                "html_length": len(content),
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            # Guardar resultado en JSON
            json_path = PathsConfig.RESEARCH_DIR / "data_samples" / f"besoccer_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Datos guardados: {json_path}\n")
            print("="*60)
            print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ ERROR: {e}\n")
            
        finally:
            await browser.close()
            print("🔒 Navegador cerrado\n")


async def test_scraper_transfermarkt():
    """
    Prueba básica de scraping en Transfermarkt
    Objetivo: Verificar si podemos acceder sin ser bloqueados por Cloudflare
    """
    
    print("\n" + "="*60)
    print("🕷️  SCRAPER DE PRUEBA - TRANSFERMARKT")
    print("="*60 + "\n")
    
    url = "https://www.transfermarkt.es"
    
    async with async_playwright() as p:
        print("🌐 Lanzando navegador...")
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=1000
        )
        
        context = await browser.new_context(
            user_agent=ScrapingConfig.USER_AGENT,
            viewport={"width": 1920, "height": 1080},
            locale="es-ES"
        )
        
        page = await context.new_page()
        
        try:
            print(f"📍 Navegando a: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Esperar más tiempo para ver si hay Cloudflare challenge
            await page.wait_for_timeout(5000)
            
            # Verificar si estamos en página de verificación
            page_content = await page.content()
            
            if "cloudflare" in page_content.lower() or "challenge" in page_content.lower():
                print("⚠️  Detectado: Página de verificación Cloudflare")
                print("💡 Estrategias futuras: Usar proxies, stealth mode, etc.\n")
            else:
                title = await page.title()
                print(f"✅ Acceso exitoso - Título: {title}\n")
            
            # Screenshot
            screenshot_path = PathsConfig.RESEARCH_DIR / "data_samples" / f"transfermarkt_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"📸 Screenshot guardado: {screenshot_path}\n")
            
        except Exception as e:
            print(f"❌ ERROR: {e}\n")
            
        finally:
            await browser.close()
            print("🔒 Navegador cerrado\n")


if __name__ == "__main__":
    print("\n🚀 INICIANDO PRUEBAS DE SCRAPING\n")
    
    # Probar BeSoccer primero (más amigable)
    asyncio.run(test_scraper_besoccer())
    
    # Descomentar para probar Transfermarkt
    # print("\n" + "─"*60 + "\n")
    # asyncio.run(test_scraper_transfermarkt())
    
    print("\n✅ TODAS LAS PRUEBAS COMPLETADAS\n")
