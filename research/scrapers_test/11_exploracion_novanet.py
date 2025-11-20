"""
==========================================
SPRINT 5: EXPLORACIÓN - Novanet (Federaciones Territoriales)
==========================================
Objetivo: Intentar acceder a datos públicos de Novanet en federaciones territoriales
ADVERTENCIA: Novanet tiene protecciones anti-scraping. Este script es exploratorio.
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime

# CONFIGURACIÓN: Federaciones a probar
FEDERACIONES_PROBAR = [
    {
        "nombre": "Murcia",
        "url_clasificacion": "https://webffrm.novanet.es/pnfg/NPcd/NFG_CmpJornada?CodCompeticion=7922114&CodGrupo=7922132&CodTemporada=20&cod_primaria=1000120",
        "url_goleadores": "https://webffrm.novanet.es/pnfg/NPcd/NFG_CMP_Goleadores?cod_primaria=1000120&CodJornada=1&codcompeticion=6858761&codtemporada=14&codgrupo=6858762"
    },
    {
        "nombre": "Castilla y León",
        "url_clasificacion": "http://www.fcylf.novanet.es/pnfg/NPcd/NFG_CmpJornada?cod_primaria=1000120&CodCompeticion=12036&CodGrupo=49374&CodTemporada=18&CodJornada=27"
    },
    {
        "nombre": "Navarra",
        "url_base": "http://www.fnf.novanet.es/pnfg/"
    }
]


async def probar_acceso_url(page, federacion, url, tipo="clasificacion"):
    """Intenta acceder a una URL de Novanet"""
    print(f"\n   🔍 Probando: {tipo}")
    print(f"      URL: {url[:80]}...")

    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        status = response.status

        print(f"      Status HTTP: {status}")

        if status == 403:
            print(f"      ❌ Error 403 (Forbidden) - Protección anti-scraping")
            return {"accesible": False, "error": "403 Forbidden", "tipo": tipo}

        elif status == 404:
            print(f"      ❌ Error 404 (Not Found) - URL no existe")
            return {"accesible": False, "error": "404 Not Found", "tipo": tipo}

        elif status >= 400:
            print(f"      ❌ Error {status}")
            return {"accesible": False, "error": f"HTTP {status}", "tipo": tipo}

        # Si llegamos aquí, intentar parsear contenido
        await page.wait_for_timeout(2000)
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # Buscar tablas
        tablas = soup.find_all('table')
        print(f"      ✅ Accesible - Tablas encontradas: {len(tablas)}")

        if not tablas:
            print(f"      ⚠️  Sin tablas (puede ser página de login o error)")
            return {"accesible": True, "sin_datos": True, "tipo": tipo}

        # Analizar primera tabla
        tabla = tablas[0]
        headers = [th.get_text(strip=True) for th in tabla.find_all('th')]
        filas = tabla.find_all('tr')

        print(f"      📋 Headers: {headers[:5]}")
        print(f"      📊 Filas: {len(filas)}")

        return {
            "accesible": True,
            "tipo": tipo,
            "num_tablas": len(tablas),
            "headers": headers,
            "num_filas": len(filas),
            "html_preview": content[:1000]
        }

    except Exception as e:
        error_msg = str(e)[:100]
        print(f"      ❌ Error: {error_msg}")
        return {"accesible": False, "error": error_msg, "tipo": tipo}


async def explorar_federacion(page, federacion):
    """Explora todas las URLs de una federación"""
    print(f"\n{'='*70}")
    print(f"🏛️  FEDERACIÓN: {federacion['nombre']}")
    print(f"{'='*70}")

    resultados = {
        "federacion": federacion["nombre"],
        "fecha": datetime.now().isoformat(),
        "urls_probadas": []
    }

    # Probar clasificación
    if "url_clasificacion" in federacion:
        resultado = await probar_acceso_url(
            page,
            federacion,
            federacion["url_clasificacion"],
            tipo="clasificacion"
        )
        resultados["urls_probadas"].append({
            "url": federacion["url_clasificacion"],
            "resultado": resultado
        })
        await asyncio.sleep(3)

    # Probar goleadores
    if "url_goleadores" in federacion:
        resultado = await probar_acceso_url(
            page,
            federacion,
            federacion["url_goleadores"],
            tipo="goleadores"
        )
        resultados["urls_probadas"].append({
            "url": federacion["url_goleadores"],
            "resultado": resultado
        })
        await asyncio.sleep(3)

    # Probar URL base
    if "url_base" in federacion:
        resultado = await probar_acceso_url(
            page,
            federacion,
            federacion["url_base"],
            tipo="base"
        )
        resultados["urls_probadas"].append({
            "url": federacion["url_base"],
            "resultado": resultado
        })

    return resultados


async def main():
    print("\n" + "="*70)
    print("🔬 EXPLORACIÓN: Novanet - Federaciones Territoriales")
    print("="*70)
    print("\n⚠️  ADVERTENCIA:")
    print("   Novanet es un sistema interno de gestión federativa.")
    print("   Es probable que encontremos protecciones anti-scraping (403).")
    print("   Este script es EXPLORATORIO para verificar accesibilidad.\n")

    async with async_playwright() as p:
        print("🦊 Lanzando Firefox...")
        browser = await p.firefox.launch(headless=True, timeout=60000)

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-ES'
        )

        page = await context.new_page()

        resultados_globales = {
            "fuente": "Novanet",
            "fecha_exploracion": datetime.now().isoformat(),
            "federaciones": []
        }

        # Explorar cada federación
        for federacion in FEDERACIONES_PROBAR:
            resultado = await explorar_federacion(page, federacion)
            resultados_globales["federaciones"].append(resultado)
            await asyncio.sleep(5)  # Delay entre federaciones

        await browser.close()
        print("\n✅ Firefox cerrado")

        # RESUMEN FINAL
        print(f"\n{'='*70}")
        print(f"📊 RESUMEN DE HALLAZGOS - Novanet")
        print(f"{'='*70}\n")

        urls_accesibles = 0
        urls_bloqueadas = 0
        urls_error = 0

        for fed_resultado in resultados_globales["federaciones"]:
            print(f"\n🏛️  {fed_resultado['federacion']}:")

            for url_data in fed_resultado["urls_probadas"]:
                resultado = url_data["resultado"]

                if resultado.get("accesible"):
                    if resultado.get("sin_datos"):
                        print(f"   ⚠️  {resultado['tipo']}: Accesible pero sin datos")
                        urls_accesibles += 1
                    else:
                        print(f"   ✅ {resultado['tipo']}: Accesible ({resultado.get('num_tablas', 0)} tablas)")
                        urls_accesibles += 1
                else:
                    if "403" in resultado.get("error", ""):
                        print(f"   ❌ {resultado['tipo']}: Bloqueado (403)")
                        urls_bloqueadas += 1
                    else:
                        print(f"   ❌ {resultado['tipo']}: Error ({resultado.get('error', 'Unknown')})")
                        urls_error += 1

        print(f"\n{'='*70}")
        print(f"📈 ESTADÍSTICAS GLOBALES")
        print(f"{'='*70}\n")
        print(f"   URLs probadas: {urls_accesibles + urls_bloqueadas + urls_error}")
        print(f"   ✅ Accesibles: {urls_accesibles}")
        print(f"   ❌ Bloqueadas (403): {urls_bloqueadas}")
        print(f"   ❌ Otros errores: {urls_error}")

        # Guardar resultados
        output_file = f"research/data_samples/analisis_ligas/exploracion_novanet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultados_globales, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultados detallados guardados en:")
        print(f"   {output_file}")

        print(f"\n{'='*70}")
        print(f"💡 CONCLUSIÓN")
        print(f"{'='*70}\n")

        if urls_bloqueadas > urls_accesibles:
            print("❌ Novanet tiene PROTECCIONES ANTI-SCRAPING activas.")
            print("   Recomendación: NO usar Novanet como fuente de datos.")
            print("   Alternativa: Usar BeSoccer, LaPreferente, FutbolMe.")
        elif urls_accesibles > 0:
            print("✅ Algunas URLs de Novanet son ACCESIBLES.")
            print("   Acción: Revisar JSON para ver qué datos están disponibles.")
            print("   Considerar: Crear scrapers específicos por federación.")
        else:
            print("⚠️  NO se pudo acceder a ninguna URL de Novanet.")
            print("   Posibles causas: URLs incorrectas, servidor caído, bloqueo total.")

        print()


if __name__ == "__main__":
    asyncio.run(main())
