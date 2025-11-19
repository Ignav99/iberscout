"""
==========================================
IBERSCOUT - DETECTIVE DE POSICIONES
==========================================
Script para encontrar exactamente dónde están las posiciones en BeSoccer
"""

import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path

# URL de prueba
URL_TEST = "https://es.besoccer.com/equipo/plantilla/mirandes"

print("\n" + "="*70)
print("🔍 DETECTIVE DE POSICIONES - BESOCCER")
print("="*70 + "\n")

print(f"📍 URL de prueba: {URL_TEST}")
print(f"🎯 Objetivo: Encontrar dónde están las posiciones de los jugadores\n")

# Descargar página
print("📡 Descargando página...")
response = requests.get(URL_TEST, headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
})

if response.status_code != 200:
    print(f"❌ Error HTTP {response.status_code}")
    exit(1)

print(f"✅ Página descargada\n")

# Parse HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Guardar HTML para análisis manual
html_path = Path("research/data_samples/analisis_ligas/detective_posiciones.html")
html_path.parent.mkdir(parents=True, exist_ok=True)
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(response.text)
print(f"💾 HTML guardado: {html_path}\n")

print("="*70)
print("MÉTODO 1: Buscar palabras clave de posiciones en TODO el HTML")
print("="*70 + "\n")

palabras_posicion = ['Portero', 'Defensa', 'Centrocampista', 'Delantero', 
                     'Porteros', 'Defensas', 'Centrocampistas', 'Delanteros']

texto_completo = soup.get_text()
encontrados = {}

for palabra in palabras_posicion:
    count = texto_completo.count(palabra)
    if count > 0:
        encontrados[palabra] = count
        print(f"✅ '{palabra}' aparece {count} veces")

if not encontrados:
    print("❌ No se encontraron palabras clave de posiciones")
else:
    print(f"\n💡 Total de menciones: {sum(encontrados.values())}")

print("\n" + "="*70)
print("MÉTODO 2: Buscar en elementos específicos (th, td, div, span)")
print("="*70 + "\n")

for etiqueta in ['th', 'td', 'div', 'span', 'h3', 'h4']:
    elementos = soup.find_all(etiqueta)
    encontrados_etiqueta = []
    
    for elem in elementos:
        texto = elem.get_text(strip=True)
        if any(pos in texto for pos in palabras_posicion):
            encontrados_etiqueta.append({
                'etiqueta': etiqueta,
                'texto': texto[:100],  # Primeros 100 caracteres
                'clases': elem.get('class', []),
                'id': elem.get('id', '')
            })
    
    if encontrados_etiqueta:
        print(f"🔍 <{etiqueta}>: {len(encontrados_etiqueta)} coincidencias")
        for i, elem in enumerate(encontrados_etiqueta[:3], 1):  # Primeras 3
            print(f"   {i}. Texto: '{elem['texto']}'")
            if elem['clases']:
                print(f"      Clases: {elem['clases']}")
            if elem['id']:
                print(f"      ID: {elem['id']}")

print("\n" + "="*70)
print("MÉTODO 3: Analizar estructura de la TABLA principal")
print("="*70 + "\n")

tablas = soup.find_all('table')
print(f"📊 Tablas encontradas: {len(tablas)}\n")

if tablas:
    tabla = tablas[0]  # Primera tabla (plantilla)
    print("🔬 ANÁLISIS DETALLADO DE LA PRIMERA TABLA:\n")
    
    filas = tabla.find_all('tr')
    print(f"   Total de filas: {len(filas)}\n")
    
    print("   📋 PRIMERAS 15 FILAS CON CONTENIDO COMPLETO:")
    print("   " + "-"*66)
    
    for i, fila in enumerate(filas[:15], 1):
        celdas = fila.find_all(['td', 'th'])
        num_celdas = len(celdas)
        
        # Obtener TODO el texto de la fila
        texto_fila = fila.get_text(strip=True)
        
        # Obtener contenido de cada celda
        contenido_celdas = [c.get_text(strip=True) for c in celdas]
        
        # Ver si tiene palabras de posición
        tiene_posicion = any(pos in texto_fila for pos in palabras_posicion)
        
        print(f"\n   Fila #{i} ({num_celdas} celdas){' ⭐ POSICIÓN' if tiene_posicion else ''}:")
        print(f"      Texto completo: '{texto_fila[:150]}'")
        
        if contenido_celdas:
            print(f"      Celdas: {contenido_celdas[:10]}")  # Primeras 10
        
        # Si tiene posición, analizar más a fondo
        if tiene_posicion:
            print(f"\n      🔍 ANÁLISIS PROFUNDO DE ESTA FILA:")
            
            # Ver atributos de la fila
            attrs = fila.attrs
            if attrs:
                print(f"         Atributos fila: {attrs}")
            
            # Ver estructura interna
            print(f"         Estructura HTML:")
            print(f"         {str(fila)[:300]}")

print("\n" + "="*70)
print("MÉTODO 4: Buscar patrones con REGEX")
print("="*70 + "\n")

# Buscar patrones como "Porteros PJ PT ..." que indican headers de sección
patron_header = re.compile(r'(Porteros|Defensas|Centrocampistas|Delanteros)\s+(PJ|PT|Edad)', re.IGNORECASE)
matches = patron_header.findall(str(soup))

if matches:
    print(f"✅ Encontrados {len(matches)} patrones de header de posición:")
    for match in matches[:5]:
        print(f"   - {match}")
else:
    print(f"❌ No se encontró el patrón esperado")

print("\n" + "="*70)
print("MÉTODO 5: Buscar en atributos data-* o title")
print("="*70 + "\n")

# Buscar elementos con data-position o similares
elementos_con_data = soup.find_all(attrs={"data-position": True})
if elementos_con_data:
    print(f"✅ Encontrados {len(elementos_con_data)} con data-position:")
    for elem in elementos_con_data[:3]:
        print(f"   - {elem.get('data-position')}: {elem.get_text(strip=True)[:50]}")
else:
    print(f"❌ No hay atributos data-position")

# Buscar titles
elementos_con_title = soup.find_all(attrs={"title": re.compile(r'(Portero|Defensa|Centrocampista|Delantero)', re.I)})
if elementos_con_title:
    print(f"\n✅ Encontrados {len(elementos_con_title)} con title de posición:")
    for elem in elementos_con_title[:3]:
        print(f"   - title='{elem.get('title')}': {elem.name} - {elem.get_text(strip=True)[:50]}")
else:
    print(f"❌ No hay atributos title con posiciones")

print("\n" + "="*70)
print("📊 RESUMEN Y CONCLUSIÓN")
print("="*70 + "\n")

print("💡 PARA ENCONTRAR LAS POSICIONES:")
print("   1. Abre el archivo HTML guardado en un navegador")
print("   2. Inspecciona manualmente un jugador portero")
print("   3. Busca en el HTML dónde dice 'Portero' o 'Porteros'")
print("   4. Identifica el patrón exacto (clase CSS, estructura)")
print("\n   Archivo HTML: research/data_samples/analisis_ligas/detective_posiciones.html")

print("\n🔍 HIPÓTESIS:")
print("   - Las posiciones pueden estar en:")
print("     • Filas separadoras entre grupos de jugadores")
print("     • Atributos ocultos (data-*, class)")
print("     • JavaScript dinámico (no visible en HTML estático)")
print("     • Tooltips o elementos hover")

print("\n" + "="*70)
print("✅ ANÁLISIS COMPLETADO")
print("="*70 + "\n")