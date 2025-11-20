"""
==========================================
EXPLORACIÓN EXHAUSTIVA: TODOS LOS DATOS DE BESOCCER
==========================================
Script para identificar TODOS los datos disponibles en fichas de BeSoccer
Basado en hallazgos del usuario:
- Tarjetas amarillas/rojas
- Altura, peso
- Valor de mercado
- Posiciones (principal/secundaria con %)
- **PUNTUACIÓN ELO** (1-100) ⭐
- Evolución temporal
- Rankings
- Rendimiento por clubes
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

URL_JUGADOR = "https://es.besoccer.com/jugador/canedo-164269"
NOMBRE = "Canedo"


async def explorar_ficha_completa(page, url):
    """Extrae ABSOLUTAMENTE TODO de la ficha de un jugador"""
    print("\n" + "="*70)
    print(f"🔬 EXPLORACIÓN EXHAUSTIVA: {NOMBRE}")
    print("="*70 + "\n")

    await page.goto(url, wait_until="networkidle", timeout=60000)
    await page.wait_for_timeout(5000)

    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')

    datos_completos = {
        "nombre": NOMBRE,
        "url": url,
        "fecha_extraccion": datetime.now().isoformat(),
        "datos_encontrados": {}
    }

    # ========================================
    # 1. DATOS PERSONALES
    # ========================================
    print("📋 DATOS PERSONALES")
    print("="*70)

    texto = soup.get_text()

    # Edad
    match_edad = re.search(r'(\d{1,2})\s*años', texto)
    if match_edad:
        datos_completos["datos_encontrados"]["edad"] = int(match_edad.group(1))
        print(f"✅ Edad: {match_edad.group(1)} años")

    # Altura
    match_altura = re.search(r'(\d{1,3})\s*cm', texto)
    if match_altura:
        datos_completos["datos_encontrados"]["altura_cm"] = int(match_altura.group(1))
        print(f"✅ Altura: {match_altura.group(1)} cm")
    else:
        print("❌ Altura: No encontrada")

    # Peso
    match_peso = re.search(r'(\d{1,3})\s*kg', texto)
    if match_peso:
        datos_completos["datos_encontrados"]["peso_kg"] = int(match_peso.group(1))
        print(f"✅ Peso: {match_peso.group(1)} kg")
    else:
        print("❌ Peso: No encontrado")

    # Nacionalidad
    match_nac = re.search(r'Nacionalidad[:\s]*([A-Za-záéíóúñÑ\s]+)', texto)
    if match_nac:
        datos_completos["datos_encontrados"]["nacionalidad"] = match_nac.group(1).strip()
        print(f"✅ Nacionalidad: {match_nac.group(1).strip()}")
    else:
        print("❌ Nacionalidad: No encontrada")

    # Pie dominante
    match_pie = re.search(r'Pie[:\s]*(Derecho|Izquierdo|Ambidiestro)', texto)
    if match_pie:
        datos_completos["datos_encontrados"]["pie_dominante"] = match_pie.group(1)
        print(f"✅ Pie dominante: {match_pie.group(1)}")
    else:
        print("❌ Pie dominante: No encontrado")

    print()

    # ========================================
    # 2. POSICIONES
    # ========================================
    print("⚽ POSICIONES")
    print("="*70)

    # Buscar posiciones con porcentajes
    # Ejemplo: "Portero 100%", "Defensa central 80%"
    posiciones_pattern = re.findall(r'(Portero|Defensa|Centrocampista|Delantero|Lateral|Central|Extremo|Pivote)[^0-9]*(\d{1,3})%', texto)

    if posiciones_pattern:
        datos_completos["datos_encontrados"]["posiciones"] = []
        for pos, porcentaje in posiciones_pattern:
            datos_completos["datos_encontrados"]["posiciones"].append({
                "posicion": pos,
                "porcentaje": int(porcentaje)
            })
            print(f"✅ {pos}: {porcentaje}%")
    else:
        print("❌ Posiciones con %: No encontradas")

    print()

    # ========================================
    # 3. VALOR DE MERCADO
    # ========================================
    print("💰 VALOR DE MERCADO")
    print("="*70)

    # Buscar valores en euros
    # Ejemplo: "50.000 €", "1M €"
    match_valor = re.search(r'([\d\.,]+)\s*[MK]?\s*€', texto)
    if match_valor:
        valor_str = match_valor.group(1)
        print(f"✅ Valor de mercado encontrado: {match_valor.group(0)}")
        datos_completos["datos_encontrados"]["valor_mercado"] = match_valor.group(0)
    else:
        print("❌ Valor de mercado: No encontrado")

    print()

    # ========================================
    # 4. PUNTUACIÓN ELO ⭐⭐⭐
    # ========================================
    print("⭐ PUNTUACIÓN ELO (BESOCCER)")
    print("="*70)

    # Buscar "ELO" en tablas
    tablas = soup.find_all('table')
    elo_encontrado = False

    for idx, tabla in enumerate(tablas, 1):
        headers = [th.get_text(strip=True) for th in tabla.find_all('th')]
        headers_lower = [h.lower() for h in headers]

        if 'elo' in headers_lower:
            print(f"✅ Tabla {idx} contiene ELO")
            idx_elo = headers_lower.index('elo')
            print(f"   Índice ELO: {idx_elo} (Header: '{headers[idx_elo]}')")

            # Extraer primera fila
            filas = tabla.find_all('tr')
            if len(filas) > 1:
                fila_datos = filas[1]
                celdas = fila_datos.find_all('td')

                if len(celdas) > idx_elo:
                    elo_valor = celdas[idx_elo].get_text(strip=True)
                    print(f"   ⭐⭐⭐ ELO ACTUAL: {elo_valor}")

                    # Extraer todas las filas para ver evolución
                    print(f"   📊 Evolución temporal:")
                    datos_completos["datos_encontrados"]["elo_historico"] = []

                    for fila in filas[1:6]:  # Primeras 5 temporadas
                        celdas_fila = fila.find_all('td')
                        if len(celdas_fila) > idx_elo:
                            # Buscar temporada (suele estar en columna 1)
                            temporada = celdas_fila[1].get_text(strip=True) if len(celdas_fila) > 1 else "?"
                            elo = celdas_fila[idx_elo].get_text(strip=True)

                            print(f"      {temporada}: {elo}")

                            datos_completos["datos_encontrados"]["elo_historico"].append({
                                "temporada": temporada,
                                "elo": elo
                            })

            elo_encontrado = True
            break

    if not elo_encontrado:
        print("❌ ELO: No encontrado en tablas")

    print()

    # ========================================
    # 5. TARJETAS AMARILLAS Y ROJAS
    # ========================================
    print("🟨🟥 TARJETAS")
    print("="*70)

    # Buscar en tablas
    tarjetas_encontradas = False

    for idx, tabla in enumerate(tablas, 1):
        headers = [th.get_text(strip=True) for th in tabla.find_all('th')]
        texto_headers = ' '.join(headers).lower()

        # Buscar iconos o texto de tarjetas
        if 'amarilla' in texto_headers or 'roja' in texto_headers or '🟨' in str(tabla) or '🟥' in str(tabla):
            print(f"✅ Tabla {idx} contiene información de tarjetas")
            print(f"   Headers: {headers}")

            # Buscar índices
            idx_amarillas = None
            idx_rojas = None

            for i, h in enumerate(headers):
                if 'amarilla' in h.lower() or '🟨' in h:
                    idx_amarillas = i
                if 'roja' in h.lower() or '🟥' in h:
                    idx_rojas = i

            if idx_amarillas is not None or idx_rojas is not None:
                filas = tabla.find_all('tr')
                if len(filas) > 1:
                    fila_datos = filas[1]
                    celdas = fila_datos.find_all('td')

                    if idx_amarillas and len(celdas) > idx_amarillas:
                        amarillas = celdas[idx_amarillas].get_text(strip=True)
                        print(f"   🟨 Tarjetas amarillas: {amarillas}")
                        datos_completos["datos_encontrados"]["tarjetas_amarillas"] = amarillas

                    if idx_rojas and len(celdas) > idx_rojas:
                        rojas = celdas[idx_rojas].get_text(strip=True)
                        print(f"   🟥 Tarjetas rojas: {rojas}")
                        datos_completos["datos_encontrados"]["tarjetas_rojas"] = rojas

            tarjetas_encontradas = True

    if not tarjetas_encontradas:
        print("❌ Tarjetas: No encontradas en tablas")

    print()

    # ========================================
    # 6. MINUTOS JUGADOS (confirmación)
    # ========================================
    print("⏱️  MINUTOS JUGADOS")
    print("="*70)

    for idx, tabla in enumerate(tablas, 1):
        headers = [th.get_text(strip=True) for th in tabla.find_all('th')]
        headers_lower = [h.lower() for h in headers]

        if 'min' in headers_lower:
            idx_min = next(i for i, h in enumerate(headers_lower) if 'min' in h)

            filas = tabla.find_all('tr')
            if len(filas) > 1:
                fila_datos = filas[1]
                celdas = fila_datos.find_all('td')

                if len(celdas) > idx_min:
                    minutos = celdas[idx_min].get_text(strip=True).replace("'", "").replace(".", "").replace(",", "")
                    if minutos.isdigit():
                        print(f"✅ Minutos jugados: {minutos}")
                        datos_completos["datos_encontrados"]["minutos_jugados"] = int(minutos)
                        break

    print()

    # ========================================
    # 7. RANKINGS
    # ========================================
    print("🏆 RANKINGS")
    print("="*70)

    # Buscar secciones de ranking
    rankings_text = re.findall(r'Ranking[^:]*:\s*#?\s*(\d+)', texto)
    if rankings_text:
        print(f"✅ Rankings encontrados: {len(rankings_text)}")
        for rank in rankings_text[:5]:
            print(f"   #{rank}")
        datos_completos["datos_encontrados"]["rankings"] = rankings_text
    else:
        print("❌ Rankings: No encontrados")

    print()

    # ========================================
    # 8. GUARDAR TODO
    # ========================================
    output_path = "research/data_samples/analisis_ligas/exploracion_exhaustiva.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(datos_completos, f, indent=2, ensure_ascii=False)

    print("="*70)
    print(f"💾 DATOS COMPLETOS GUARDADOS EN:")
    print(f"   {output_path}")
    print("="*70 + "\n")

    # RESUMEN
    print("📊 RESUMEN DE HALLAZGOS")
    print("="*70)
    total_campos = len(datos_completos["datos_encontrados"])
    print(f"✅ Total campos extraídos: {total_campos}\n")

    for campo, valor in datos_completos["datos_encontrados"].items():
        if isinstance(valor, list):
            print(f"   • {campo}: {len(valor)} items")
        else:
            print(f"   • {campo}: {valor}")

    print()

    return datos_completos


async def main():
    print("\n🔬 EXPLORACIÓN EXHAUSTIVA DE BESOCCER")
    print("="*70)
    print("Objetivo: Identificar TODOS los datos disponibles\n")

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False, timeout=60000)

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-ES'
        )

        page = await context.new_page()

        datos = await explorar_ficha_completa(page, URL_JUGADOR)

        print("\n⏸️  Presiona ENTER para cerrar...")
        input()

        await browser.close()

        print("\n🎉 Exploración completada")
        print("\nPróximos pasos:")
        print("1. Revisar JSON generado")
        print("2. Actualizar schema de BD con nuevos campos")
        print("3. Crear script de extracción completo\n")


if __name__ == "__main__":
    asyncio.run(main())
