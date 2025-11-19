"""
==========================================
IBERSCOUT - SCRAPER DEFINITIVO CON FIREFOX
==========================================
Versión final: Firefox headless + Extracción completa
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("research/data_samples/analisis_ligas")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EQUIPOS_PRUEBA = {
    "Segunda División": {
        "nombre": "CD Mirandés",
        "url": "https://es.besoccer.com/equipo/plantilla/mirandes"
    },
    "1ª RFEF": {
        "nombre": "Real Sociedad B",
        "url": "https://es.besoccer.com/equipo/plantilla/real-sociedad-b"
    },
    "2ª RFEF": {
        "nombre": "Tudelano",
        "url": "https://es.besoccer.com/equipo/plantilla/tudelano"
    },
    "3ª RFEF": {
        "nombre": "Utebo",
        "url": "https://es.besoccer.com/equipo/plantilla/utebo"
    }
}


async def extraer_equipo_besoccer(liga, equipo_info, browser):
    """
    Extrae jugadores de un equipo usando Firefox
    """
    print(f"\n{'='*70}")
    print(f"🔍 {liga} - {equipo_info['nombre']}")
    print(f"{'='*70}")
    
    try:
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-ES'
        )
        
        page = await context.new_page()
        
        print(f"📡 Navegando a {equipo_info['url']}...")
        await page.goto(equipo_info['url'], wait_until="networkidle", timeout=60000)
        
        print(f"⏳ Esperando contenido dinámico...")
        await page.wait_for_timeout(3000)
        
        # Obtener HTML
        content = await page.content()
        
        # Parsear con BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        tablas = soup.find_all('table')
        
        if not tablas:
            print(f"❌ No se encontraron tablas")
            await context.close()
            return []
        
        print(f"✅ Tabla encontrada")
        
        # Extraer jugadores
        tabla = tablas[0]
        filas = tabla.find_all('tr')
        
        jugadores = []
        posicion_actual = None
        posiciones_detectadas = []
        
        mapeo_posiciones = {
            'Porteros': 'Portero',
            'Portero': 'Portero',
            'Defensas': 'Defensa',
            'Defensa': 'Defensa',
            'Centrocampistas': 'Centrocampista',
            'Centrocampista': 'Centrocampista',
            'Delanteros': 'Delantero',
            'Delantero': 'Delantero'
        }
        
        for fila in filas:
            celdas = fila.find_all(['td', 'th'])
            num_celdas = len(celdas)
            
            if num_celdas == 0:
                continue
            
            datos = [c.get_text(strip=True) for c in celdas]
            
            # Detectar fila de posición (contiene palabras clave)
            texto_fila = ' '.join(datos)
            for pos_key, pos_valor in mapeo_posiciones.items():
                if pos_key in texto_fila and 'PJ' in texto_fila:
                    posicion_actual = pos_valor
                    if pos_valor not in posiciones_detectadas:
                        posiciones_detectadas.append(pos_valor)
                        print(f"   📌 {pos_valor}")
                    break
            
            # Detectar fila de jugador (empieza con número)
            if not datos[0].isdigit():
                continue
            
            # Extraer datos del jugador
            # Estructura BeSoccer:
            # 0: Dorsal, 2: Nombre, 4: PJ, 5: PT, 6: Goles, 7: Asistencias, 9: Edad
            jugador = {
                "dorsal": int(datos[0]) if datos[0].isdigit() else None,
                "nombre": datos[2] if len(datos) > 2 else "",
                "posicion": posicion_actual,
                "partidos_jugados": int(datos[4]) if len(datos) > 4 and datos[4].isdigit() else 0,
                "partidos_titular": int(datos[5]) if len(datos) > 5 and datos[5].isdigit() else 0,
                "goles": int(datos[6]) if len(datos) > 6 and datos[6].isdigit() else 0,
                "asistencias": int(datos[7]) if len(datos) > 7 and datos[7].isdigit() else 0,
                "edad": int(datos[9]) if len(datos) > 9 and datos[9].isdigit() else None,
                "equipo": equipo_info['nombre'],
                "liga": liga
            }
            
            jugadores.append(jugador)
        
        print(f"✅ {len(jugadores)} jugadores extraídos")
        
        if posiciones_detectadas:
            print(f"   Posiciones: {', '.join(posiciones_detectadas)}")
        else:
            print(f"   ⚠️  No se detectaron posiciones")
        
        # Mostrar ejemplos
        if jugadores:
            print(f"\n   📋 PRIMEROS 3 JUGADORES:")
            for i, jug in enumerate(jugadores[:3], 1):
                pos = jug['posicion'] or '❌'
                edad = f"{jug['edad']}a" if jug['edad'] else '?'
                print(f"      {i}. {jug['nombre']} (#{jug['dorsal']}) - {pos} - {edad} - {jug['partidos_jugados']} PJ")
        
        await context.close()
        return jugadores
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await context.close()
        except:
            pass
        return []


async def main():
    """
    Extrae jugadores de todas las ligas
    """
    print("\n" + "🏆"*35)
    print("   IBERSCOUT - EXTRACCIÓN DEFINITIVA")
    print("🏆"*35 + "\n")
    
    print("🎯 Objetivo: Extraer plantillas completas con posiciones")
    print("🦊 Método: Firefox headless (sin ventana)")
    print("📊 Equipos: 4 (Segunda, 1ª RFEF, 2ª RFEF, 3ª RFEF)\n")
    
    input("Presiona ENTER para comenzar...")
    
    # Lanzar Firefox UNA sola vez (reutilizar)
    async with async_playwright() as p:
        print("\n🦊 Lanzando Firefox en modo headless...")
        browser = await p.firefox.launch(
            headless=True,  # ← SIN VENTANA
            timeout=60000
        )
        print("✅ Firefox listo\n")
        
        todos_jugadores = []
        resumen = {}
        
        for liga, equipo_info in EQUIPOS_PRUEBA.items():
            jugadores = await extraer_equipo_besoccer(liga, equipo_info, browser)
            todos_jugadores.extend(jugadores)
            resumen[liga] = {
                "jugadores": len(jugadores),
                "con_posicion": sum(1 for j in jugadores if j['posicion'])
            }
        
        await browser.close()
        print("\n✅ Firefox cerrado")
    
    # RESUMEN GLOBAL
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN GLOBAL")
    print(f"{'='*70}\n")
    
    total = len(todos_jugadores)
    con_posicion = sum(1 for j in todos_jugadores if j['posicion'])
    
    print(f"✅ Total jugadores: {total}")
    print(f"✅ Con posición: {con_posicion}/{total} ({con_posicion/total*100:.1f}%)\n")
    
    print("Por liga:")
    for liga, stats in resumen.items():
        porc = stats['con_posicion']/stats['jugadores']*100 if stats['jugadores'] > 0 else 0
        print(f"   {liga}:")
        print(f"      Jugadores: {stats['jugadores']}")
        print(f"      Con posición: {stats['con_posicion']} ({porc:.0f}%)")
    
    if total == 0:
        print("\n❌ No se extrajeron jugadores")
        return
    
    # Guardar datos
    print(f"\n💾 Guardando datos...")
    
    df = pd.DataFrame(todos_jugadores)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    csv_path = OUTPUT_DIR / f"jugadores_final_{timestamp}.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"   📄 CSV: {csv_path.name}")
    
    json_path = OUTPUT_DIR / f"jugadores_final_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(todos_jugadores, f, indent=2, ensure_ascii=False)
    print(f"   📄 JSON: {json_path.name}")
    
    # Estadísticas
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"   Edad promedio: {df['edad'].mean():.1f} años")
    
    print(f"   Jugadores por posición:")
    posiciones = df['posicion'].value_counts()
    for pos, count in posiciones.items():
        if pd.notna(pos):
            print(f"      {pos}: {count}")
    
    sin_posicion = df['posicion'].isna().sum()
    if sin_posicion > 0:
        print(f"      ❌ Sin posición: {sin_posicion}")
    
    print(f"\n🎉 ¡EXTRACCIÓN COMPLETADA!")
    print(f"📁 Archivos en: {OUTPUT_DIR}\n")


if __name__ == "__main__":
    asyncio.run(main())