"""
==========================================
DEBUG: Detectar registros problemáticos
==========================================
Identifica valores que causan "integer out of range" en PostgreSQL
"""

import pandas as pd
from pathlib import Path
import numpy as np

# Rutas
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "research" / "data_samples" / "analisis_ligas"

# Límites de INTEGER en PostgreSQL
INT_MIN = -2147483648
INT_MAX = 2147483647


def encontrar_csv_mas_reciente():
    """Encuentra el CSV más reciente"""
    archivos_csv = list(DATA_DIR.glob("jugadores_final_*.csv"))
    if not archivos_csv:
        return None
    return sorted(archivos_csv, key=lambda x: x.stat().st_mtime, reverse=True)[0]


def analizar_csv(csv_file):
    """Analiza el CSV en busca de valores problemáticos"""
    print("=" * 70)
    print("🔍 ANÁLISIS DE CSV - DETECCIÓN DE PROBLEMAS")
    print("=" * 70)
    print(f"\n📁 Archivo: {csv_file.name}\n")

    # Leer CSV
    df = pd.read_csv(csv_file)
    print(f"✅ Registros totales: {len(df)}")
    print(f"📋 Columnas: {', '.join(df.columns.tolist())}\n")

    # Mostrar info de tipos
    print("📊 INFORMACIÓN DE TIPOS DE DATOS:")
    print("-" * 70)
    print(df.dtypes)
    print()

    problemas = []

    # Revisar columnas numéricas
    columnas_numericas = ['dorsal', 'partidos_jugados', 'partidos_titular', 'goles', 'asistencias', 'edad']

    print("🔍 ANÁLISIS DE COLUMNAS NUMÉRICAS:")
    print("-" * 70)

    for col in columnas_numericas:
        if col not in df.columns:
            print(f"⚠️  Columna '{col}' no encontrada")
            continue

        print(f"\n📌 {col.upper()}:")

        # Estadísticas
        valores_no_nulos = df[col].dropna()
        print(f"   • Valores no-nulos: {len(valores_no_nulos)}")
        print(f"   • Valores nulos: {df[col].isna().sum()}")

        if len(valores_no_nulos) > 0:
            print(f"   • Mínimo: {valores_no_nulos.min()}")
            print(f"   • Máximo: {valores_no_nulos.max()}")
            print(f"   • Tipo Python: {type(valores_no_nulos.iloc[0])}")

            # Detectar valores fuera de rango INTEGER
            fuera_rango = df[(df[col].notna()) & ((df[col] < INT_MIN) | (df[col] > INT_MAX))]
            if len(fuera_rango) > 0:
                print(f"   ❌ PROBLEMA: {len(fuera_rango)} valores fuera de rango INTEGER")
                problemas.append({
                    'columna': col,
                    'registros': fuera_rango
                })

            # Detectar valores no enteros (floats con decimales)
            if df[col].dtype == 'float64':
                no_enteros = df[df[col].notna() & (df[col] != df[col].astype(int))]
                if len(no_enteros) > 0:
                    print(f"   ⚠️  {len(no_enteros)} valores con decimales (deberían ser enteros)")

    # Mostrar registros problemáticos
    if problemas:
        print("\n" + "=" * 70)
        print("❌ REGISTROS PROBLEMÁTICOS DETECTADOS:")
        print("=" * 70)

        for i, problema in enumerate(problemas, 1):
            print(f"\n{i}. Columna: {problema['columna']}")
            print(f"   Registros afectados: {len(problema['registros'])}")
            print()
            for idx, row in problema['registros'].iterrows():
                print(f"   Fila {idx}:")
                print(f"      • Nombre: {row.get('nombre', 'N/A')}")
                print(f"      • Equipo: {row.get('equipo', 'N/A')}")
                print(f"      • {problema['columna']}: {row[problema['columna']]}")
                print()
    else:
        print("\n✅ No se detectaron valores fuera de rango INTEGER")

    # Análisis adicional: buscar NaN y tipos raros
    print("\n" + "=" * 70)
    print("🔍 ANÁLISIS ADICIONAL:")
    print("=" * 70)

    print("\nValores únicos en cada columna numérica:")
    for col in columnas_numericas:
        if col in df.columns:
            unicos = df[col].nunique()
            print(f"   • {col}: {unicos} valores únicos")

    # Mostrar primeros 5 registros
    print("\n📋 PRIMEROS 5 REGISTROS:")
    print("-" * 70)
    print(df.head())

    # Mostrar últimos 5 registros
    print("\n📋 ÚLTIMOS 5 REGISTROS:")
    print("-" * 70)
    print(df.tail())

    # Buscar valores infinitos
    print("\n🔍 BÚSQUEDA DE VALORES INFINITOS:")
    print("-" * 70)
    for col in columnas_numericas:
        if col in df.columns and df[col].dtype in ['float64', 'int64']:
            infinitos = df[np.isinf(df[col])]
            if len(infinitos) > 0:
                print(f"   ❌ {col}: {len(infinitos)} valores infinitos")
            else:
                print(f"   ✅ {col}: sin valores infinitos")

    print("\n" + "=" * 70)


def main():
    csv_file = encontrar_csv_mas_reciente()
    if not csv_file:
        print("❌ No se encontró CSV")
        return

    analizar_csv(csv_file)


if __name__ == "__main__":
    main()
