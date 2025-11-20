"""
===========================================
VALIDACIÓN DE DATOS EXTRAÍDOS - SPRINT 1
===========================================
Análisis de calidad de los datos del scraper
"""

import pandas as pd
from io import StringIO

# Datos extraídos (pegados manualmente)
datos_csv = """dorsal,nombre,posicion,partidos_jugados,partidos_titular,goles,asistencias,edad,equipo,liga
1,I. Nikić,Portero,9,9,16,0,25.0,CD Mirandés,Segunda División
13,Juanpa,Portero,6,5,7,0,25.0,CD Mirandés,Segunda División
31,Ale Gorrín,Portero,0,0,0,0,23.0,CD Mirandés,Segunda División
22,Juan Gutierrez,Defensa,13,13,0,1,25.0,CD Mirandés,Segunda División
4,Martín Pascual,Defensa,11,10,0,2,26.0,CD Mirandés,Segunda División
17,Pablo Pérez,Defensa,8,7,0,0,24.0,CD Mirandés,Segunda División
21,Sergio Postigo,Defensa,7,6,0,0,37.0,CD Mirandés,Segunda División
3,F. Medrano,Defensa,9,7,0,0,25.0,CD Mirandés,Segunda División
2,Hugo Novoa,Defensa,10,9,0,0,22.0,CD Mirandés,Segunda División
24,Iker Córdoba,Defensa,12,10,0,0,20.0,CD Mirandés,Segunda División
5,Adrián Pica,Defensa,5,4,0,0,23.0,CD Mirandés,Segunda División
36,H. Alutiz,Defensa,0,0,0,0,22.0,CD Mirandés,Segunda División
47,A. Maiga,Defensa,0,0,0,0,19.0,CD Mirandés,Segunda División
43,Edu Coniac,Defensa,0,0,0,0,20.0,CD Mirandés,Segunda División
26,Rafel Bauza,Centrocampista,11,11,2,0,20.0,CD Mirandés,Segunda División
19,Marino,Centrocampista,8,6,0,0,24.0,CD Mirandés,Segunda División
18,Ismael Barea,Centrocampista,10,8,1,0,20.0,CD Mirandés,Segunda División
8,Aarón,Centrocampista,7,4,0,0,18.0,CD Mirandés,Segunda División
11,Álex Cardero,Centrocampista,10,4,1,1,22.0,CD Mirandés,Segunda División
6,Thiago Helguera,Centrocampista,12,7,0,1,19.0,CD Mirandés,Segunda División
41,M. Gracia,Centrocampista,0,0,0,0,21.0,CD Mirandés,Segunda División
35,Hugo Zárate,Centrocampista,0,0,0,0,21.0,CD Mirandés,Segunda División
10,C. Fernández,Delantero,12,9,6,2,29.0,CD Mirandés,Segunda División
9,Gonzalo Petit,Delantero,13,5,3,1,19.0,CD Mirandés,Segunda División
7,Iker Varela,Delantero,8,6,0,0,22.0,CD Mirandés,Segunda División
30,Salim El Jebari,Delantero,9,3,0,1,21.0,CD Mirandés,Segunda División
20,E. Eto'o,Delantero,6,0,0,0,23.0,CD Mirandés,Segunda División
14,Alberto Marí,Delantero,7,5,0,1,24.0,CD Mirandés,Segunda División
29,Pablo López,Delantero,4,2,1,0,19.0,CD Mirandés,Segunda División
27,T. Tamarit,Delantero,8,4,0,1,19.0,CD Mirandés,Segunda División
32,S. Gabriel,Delantero,0,0,0,0,22.0,CD Mirandés,Segunda División
1,Aitor Fraga,Portero,11,11,17,0,22.0,Real Sociedad B,1ª RFEF
13,Egoitz Arana,Portero,3,3,7,0,23.0,Real Sociedad B,1ª RFEF
32,Theo Folgado,Portero,0,0,0,0,20.0,Real Sociedad B,1ª RFEF
5,Peru Rodríguez,Defensa,12,12,2,0,23.0,Real Sociedad B,1ª RFEF
2,Iñaki Rupérez,Defensa,0,0,0,0,22.0,Real Sociedad B,1ª RFEF
4,Luken Beitia,Defensa,10,10,0,1,21.0,Real Sociedad B,1ª RFEF
3,Jon Balda,Defensa,12,8,0,0,23.0,Real Sociedad B,1ª RFEF
23,Unax Agote,Defensa,9,8,0,0,22.0,Real Sociedad B,1ª RFEF
29,Jon Garro,Defensa,9,5,0,0,20.0,Real Sociedad B,1ª RFEF
15,Kazunari Kita,Defensa,7,5,0,0,20.0,Real Sociedad B,1ª RFEF
36,Anartz Segurola,Defensa,0,0,0,0,19.0,Real Sociedad B,1ª RFEF
37,I. Calderón,Defensa,0,0,0,0,19.0,Real Sociedad B,1ª RFEF
27,E. Astigarraga,Defensa,0,0,0,0,21.0,Real Sociedad B,1ª RFEF
8,Mikel Rodriguez,Centrocampista,11,9,2,0,23.0,Real Sociedad B,1ª RFEF
14,T. Carbonell,Centrocampista,11,11,0,0,20.0,Real Sociedad B,1ª RFEF
17,L. Astiazarán,Centrocampista,13,9,3,1,19.0,Real Sociedad B,1ª RFEF
6,Alex Lebarbier,Centrocampista,8,2,1,0,21.0,Real Sociedad B,1ª RFEF
16,G. Gorosabel,Centrocampista,13,9,0,4,19.0,Real Sociedad B,1ª RFEF
30,Joni Eceizabarrena,Centrocampista,8,4,0,0,20.0,Real Sociedad B,1ª RFEF
31,I. Aguirre,Centrocampista,3,3,0,0,18.0,Real Sociedad B,1ª RFEF
34,Joan Oleaga,Centrocampista,0,0,0,0,19.0,Real Sociedad B,1ª RFEF
10,A. Mariezkurrena,Delantero,13,7,1,0,20.0,Real Sociedad B,1ª RFEF
18,Gorka Carrera,Delantero,14,10,6,3,20.0,Real Sociedad B,1ª RFEF
9,E. Orobengoa,Delantero,8,5,0,0,21.0,Real Sociedad B,1ª RFEF
19,A. Marchal,Delantero,10,4,0,0,18.0,Real Sociedad B,1ª RFEF
11,Job Ochieng,Delantero,11,7,2,2,22.0,Real Sociedad B,1ª RFEF
22,Alberto Dadie,Delantero,11,9,0,0,23.0,Real Sociedad B,1ª RFEF
7,Dani Díaz,Delantero,10,3,2,0,19.0,Real Sociedad B,1ª RFEF
26,Darío Ramírez,Delantero,1,0,0,0,20.0,Real Sociedad B,1ª RFEF
33,Jakes Gorosabel,Delantero,0,0,0,0,21.0,Real Sociedad B,1ª RFEF
20,Sydney,Delantero,3,0,1,0,18.0,Real Sociedad B,1ª RFEF
13,Yoel Ramírez,Portero,11,10,11,0,23.0,Tudelano,2ª RFEF
1,Aitor Ekiza,Portero,1,1,0,0,24.0,Tudelano,2ª RFEF
25,R. Enrique,Portero,0,0,0,0,,Tudelano,2ª RFEF
25,R. Mocian,Portero,0,0,0,0,,Tudelano,2ª RFEF
25,C. Manuel,Portero,0,0,0,0,22.0,Tudelano,2ª RFEF
19,Julen Monreal,Defensa,10,8,0,0,31.0,Tudelano,2ª RFEF
16,A. Parada,Defensa,7,7,0,0,27.0,Tudelano,2ª RFEF
3,I. Balda,Defensa,8,6,0,0,23.0,Tudelano,2ª RFEF
12,Iker Bachiller,Defensa,6,5,0,3,23.0,Tudelano,2ª RFEF
4,Asier Pérez,Defensa,9,8,1,0,22.0,Tudelano,2ª RFEF
5,Aimar Collante,Defensa,0,0,0,0,23.0,Tudelano,2ª RFEF
2,Ander Dufur,Defensa,10,10,0,0,24.0,Tudelano,2ª RFEF
14,Dani Santigosa,Centrocampista,10,9,1,0,31.0,Tudelano,2ª RFEF
6,Guille Alonso,Centrocampista,9,9,1,0,29.0,Tudelano,2ª RFEF
20,Curro Bonilla,Centrocampista,9,6,2,0,22.0,Tudelano,2ª RFEF
18,Albín,Centrocampista,11,11,0,0,24.0,Tudelano,2ª RFEF
8,M. Vila,Centrocampista,8,5,1,0,19.0,Tudelano,2ª RFEF
21,A. Kessas,Centrocampista,6,0,0,0,21.0,Tudelano,2ª RFEF
24,J. Quattrocchi,Centrocampista,4,0,0,0,21.0,Tudelano,2ª RFEF
17,I. Alayeto,Delantero,8,7,6,0,31.0,Tudelano,2ª RFEF
10,David Aparicio,Delantero,11,11,0,0,29.0,Tudelano,2ª RFEF
23,T. Bouguettaya,Delantero,11,6,4,0,20.0,Tudelano,2ª RFEF
7,I. Boudaoud,Delantero,7,0,0,1,23.0,Tudelano,2ª RFEF
22,Miguel Clavería,Delantero,4,0,1,0,21.0,Tudelano,2ª RFEF
9,Simón Moreno,Delantero,5,0,0,0,28.0,Tudelano,2ª RFEF
11,Nowend Lorenzo,Delantero,8,2,0,0,23.0,Tudelano,2ª RFEF
1,J. Chanza,Portero,8,8,8,0,27.0,Utebo,3ª RFEF
13,Pol,Portero,3,3,5,0,22.0,Utebo,3ª RFEF
4,Meseguer,Defensa,10,10,0,0,33.0,Utebo,3ª RFEF
5,Guti,Defensa,11,9,1,0,30.0,Utebo,3ª RFEF
15,Víctor Sanchis,Defensa,10,9,1,0,24.0,Utebo,3ª RFEF
6,M. Álvarez,Defensa,8,3,0,4,23.0,Utebo,3ª RFEF
22,Mendi,Defensa,2,1,0,0,30.0,Utebo,3ª RFEF
3,Franc Mateu,Defensa,10,10,0,0,21.0,Utebo,3ª RFEF
23,Alex Rodríguez,Defensa,6,3,0,1,23.0,Utebo,3ª RFEF
8,D. Marín,Centrocampista,9,6,0,2,25.0,Utebo,3ª RFEF
17,Ces Cotos,Centrocampista,11,9,2,2,25.0,Utebo,3ª RFEF
20,Camilo Leiton,Centrocampista,10,8,2,0,23.0,Utebo,3ª RFEF
11,Diego López,Centrocampista,10,3,3,3,24.0,Utebo,3ª RFEF
21,Carlos Beitia,Centrocampista,10,6,0,0,25.0,Utebo,3ª RFEF
27,D. Salas,Centrocampista,1,0,0,0,,Utebo,3ª RFEF
10,Diego Suárez,Delantero,11,10,5,0,31.0,Utebo,3ª RFEF
14,Bouba,Delantero,11,2,4,1,24.0,Utebo,3ª RFEF
19,Juan Delgado,Delantero,7,5,3,0,31.0,Utebo,3ª RFEF
9,Iñigo López,Delantero,7,6,2,2,23.0,Utebo,3ª RFEF
7,Iñaki Alberca,Delantero,7,3,1,1,21.0,Utebo,3ª RFEF
16,Pedrosa,Delantero,10,7,0,0,22.0,Utebo,3ª RFEF
28,David Rivera,Delantero,1,0,0,0,21.0,Utebo,3ª RFEF"""

# Leer los datos
df = pd.read_csv(StringIO(datos_csv))

print("\n" + "="*70)
print("📊 ANÁLISIS DE CALIDAD DE DATOS - SPRINT 1")
print("="*70 + "\n")

# 1. RESUMEN GENERAL
print("1️⃣  RESUMEN GENERAL")
print("-" * 70)
print(f"Total de jugadores: {len(df)}")
print(f"Equipos: {df['equipo'].nunique()}")
print(f"Ligas: {df['liga'].nunique()}")
print()

# Jugadores por equipo
print("Jugadores por equipo:")
for equipo, count in df['equipo'].value_counts().items():
    liga = df[df['equipo'] == equipo]['liga'].iloc[0]
    print(f"  • {equipo:20s} ({liga:20s}): {count:2d} jugadores")
print()

# 2. CALIDAD DE DATOS
print("\n2️⃣  CALIDAD DE DATOS")
print("-" * 70)

# Valores nulos
print("Valores nulos por columna:")
nulos = df.isnull().sum()
for col, count in nulos.items():
    if count > 0:
        porcentaje = (count / len(df)) * 100
        print(f"  ⚠️  {col:20s}: {count:3d} ({porcentaje:.1f}%)")
if nulos.sum() == 0:
    print("  ✅ No hay valores nulos")
print()

# 3. POSICIONES
print("\n3️⃣  DISTRIBUCIÓN POR POSICIONES")
print("-" * 70)
posiciones = df['posicion'].value_counts()
for pos, count in posiciones.items():
    porcentaje = (count / len(df)) * 100
    print(f"  {pos:20s}: {count:3d} ({porcentaje:.1f}%)")
print()

# 4. ESTADÍSTICAS DE EDAD
print("\n4️⃣  ESTADÍSTICAS DE EDAD")
print("-" * 70)
edades = df['edad'].dropna()
print(f"  Edad promedio: {edades.mean():.1f} años")
print(f"  Edad mínima: {edades.min():.0f} años")
print(f"  Edad máxima: {edades.max():.0f} años")
print(f"  Mediana: {edades.median():.0f} años")
print()

# 5. DUPLICADOS POTENCIALES
print("\n5️⃣  DETECCIÓN DE DUPLICADOS")
print("-" * 70)

# Duplicados por dorsal en mismo equipo
duplicados_dorsal = df[df.duplicated(['equipo', 'dorsal'], keep=False)]
if len(duplicados_dorsal) > 0:
    print(f"  ⚠️  {len(duplicados_dorsal)} jugadores con dorsal duplicado:")
    for _, row in duplicados_dorsal.iterrows():
        print(f"      • {row['equipo']:20s} - #{row['dorsal']:2.0f} {row['nombre']}")
else:
    print("  ✅ No hay dorsales duplicados por equipo")
print()

# Duplicados por nombre en mismo equipo
duplicados_nombre = df[df.duplicated(['equipo', 'nombre'], keep=False)]
if len(duplicados_nombre) > 0:
    print(f"  ⚠️  {len(duplicados_nombre)} jugadores con nombre duplicado")
else:
    print("  ✅ No hay nombres duplicados por equipo")
print()

# 6. DATOS ESTADÍSTICOS
print("\n6️⃣  ESTADÍSTICAS DEPORTIVAS")
print("-" * 70)
print(f"  Partidos jugados (promedio): {df['partidos_jugados'].mean():.1f}")
print(f"  Goles totales: {df['goles'].sum():.0f}")
print(f"  Asistencias totales: {df['asistencias'].sum():.0f}")
print()

# Máximos goleadores
print("  Top 5 goleadores:")
top_goleadores = df.nlargest(5, 'goles')[['nombre', 'equipo', 'posicion', 'goles']]
for idx, row in top_goleadores.iterrows():
    print(f"    {row['nombre']:20s} ({row['posicion']:15s}) - {row['goles']:.0f} goles")
print()

# 7. PROBLEMAS DETECTADOS
print("\n7️⃣  PROBLEMAS DETECTADOS")
print("-" * 70)

problemas = []

# Jugadores sin edad
sin_edad = df[df['edad'].isnull()]
if len(sin_edad) > 0:
    problemas.append(f"⚠️  {len(sin_edad)} jugadores sin edad ({len(sin_edad)/len(df)*100:.1f}%)")

# Jugadores sin partidos pero con goles
sin_partidos_con_goles = df[(df['partidos_jugados'] == 0) & (df['goles'] > 0)]
if len(sin_partidos_con_goles) > 0:
    problemas.append(f"⚠️  {len(sin_partidos_con_goles)} jugadores con goles pero sin partidos jugados")

# Dorsales duplicados
if len(duplicados_dorsal) > 0:
    problemas.append(f"⚠️  {len(duplicados_dorsal)} dorsales duplicados (probablemente error de scraping)")

if len(problemas) > 0:
    for problema in problemas:
        print(f"  {problema}")
else:
    print("  ✅ No se detectaron problemas críticos")
print()

# 8. CALIFICACIÓN FINAL
print("\n8️⃣  CALIFICACIÓN FINAL")
print("-" * 70)

# Calcular puntuación
puntuacion = 100
if len(sin_edad) > 0:
    puntuacion -= min((len(sin_edad) / len(df)) * 100 * 2, 20)  # Max -20 puntos
if len(duplicados_dorsal) > 0:
    puntuacion -= min((len(duplicados_dorsal) / len(df)) * 100 * 3, 30)  # Max -30 puntos
if nulos.sum() > 0:
    puntuacion -= min((nulos.sum() / (len(df) * len(df.columns))) * 100, 10)  # Max -10 puntos

print(f"  Calidad de datos: {puntuacion:.0f}/100")
print()

if puntuacion >= 90:
    print("  ✅ EXCELENTE - Los datos son de muy alta calidad")
    print("  ✅ Recomendación: Continuar al Sprint 2 (Carga en PostgreSQL)")
elif puntuacion >= 75:
    print("  ✅ BUENA - Los datos son aceptables con problemas menores")
    print("  ⚠️  Recomendación: Documentar problemas y continuar al Sprint 2")
elif puntuacion >= 60:
    print("  ⚠️  REGULAR - Hay varios problemas que deberían corregirse")
    print("  ⚠️  Recomendación: Revisar scraper antes de continuar")
else:
    print("  ❌ BAJA - Los datos tienen problemas significativos")
    print("  ❌ Recomendación: Revisar y corregir scraper antes de continuar")

print("\n" + "="*70)
print("✅ ANÁLISIS COMPLETADO")
print("="*70 + "\n")
