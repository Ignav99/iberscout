"""
==========================================
SPRINT 3: FUZZY MATCHING - PRUEBA DE CONCEPTO
==========================================
Valida que el algoritmo funciona con dataset de prueba antes de aplicarlo a BD
"""

from thefuzz import fuzz
from thefuzz import process
import pandas as pd

print("\n" + "="*70)
print("🔍 SPRINT 3: FUZZY MATCHING - PRUEBA DE CONCEPTO")
print("="*70 + "\n")

# ==============================================================================
# DATASET DE PRUEBA - Casos reales de nombres con variaciones
# ==============================================================================

DATASET_PRUEBA = [
    # Caso 1: Iniciales vs Nombre completo
    ("J. Bellingham", "Jude Bellingham", True),  # Mismo jugador
    ("L. Messi", "Lionel Messi", True),
    ("C. Ronaldo", "Cristiano Ronaldo", True),

    # Caso 2: Abreviaturas
    ("Leo Messi", "Lionel Messi", True),
    ("Vini Jr", "Vinicius Junior", True),

    # Caso 3: Con acentos vs sin acentos
    ("José García", "Jose Garcia", True),
    ("Álvaro Pérez", "Alvaro Perez", True),

    # Caso 4: Nombres compuestos
    ("Juan Carlos López", "J.C. López", True),
    ("Miguel Ángel", "M. Ángel", True),

    # Caso 5: DIFÍCIL - Nombres muy similares pero DIFERENTES jugadores
    ("J. García", "José García", False),  # ¿Es Juan o José? No sabemos
    ("A. González", "Antonio González", False),  # Podría ser Alberto, Andrés...

    # Caso 6: Nombres completamente diferentes
    ("Messi", "Cristiano", False),
    ("Benzema", "Lewandowski", False),

    # Caso 7: Apellidos dobles
    ("Sergio Ramos García", "S. Ramos", True),
    ("Marc-André ter Stegen", "Ter Stegen", True),

    # Caso 8: Apodos vs nombre real
    ("Vinicius", "Vini", True),  # Caso común en Brasil
    ("Rodrygo", "Rodry", True),

    # Caso 9: Con sufijos
    ("John Smith Jr.", "John Smith", True),
    ("David Villa", "D. Villa", True),
]

print(f"📊 Dataset de prueba: {len(DATASET_PRUEBA)} pares de nombres\n")

# ==============================================================================
# ALGORITMOS DE FUZZY MATCHING A PROBAR
# ==============================================================================

ALGORITMOS = {
    "ratio": fuzz.ratio,
    "partial_ratio": fuzz.partial_ratio,
    "token_sort_ratio": fuzz.token_sort_ratio,
    "token_set_ratio": fuzz.token_set_ratio,
}

print("🧪 Algoritmos a probar:")
for i, nombre in enumerate(ALGORITMOS.keys(), 1):
    print(f"   {i}. {nombre}")
print()

# ==============================================================================
# EVALUAR CADA ALGORITMO
# ==============================================================================

resultados = []

for nombre_algo, funcion_algo in ALGORITMOS.items():
    print(f"\n{'='*70}")
    print(f"🔬 PROBANDO: {nombre_algo}")
    print(f"{'='*70}\n")

    for nombre1, nombre2, son_mismo in DATASET_PRUEBA:
        similitud = funcion_algo(nombre1, nombre2)

        resultados.append({
            "algoritmo": nombre_algo,
            "nombre1": nombre1,
            "nombre2": nombre2,
            "similitud": similitud,
            "son_mismo_real": son_mismo,
        })

        print(f"{similitud:3d}% | {nombre1:30s} ←→ {nombre2:30s} | Real: {son_mismo}")

# ==============================================================================
# ANÁLISIS DE RESULTADOS
# ==============================================================================

print(f"\n{'='*70}")
print("📈 ANÁLISIS DE RESULTADOS")
print(f"{'='*70}\n")

df = pd.DataFrame(resultados)

# Probar diferentes umbrales
UMBRALES = [70, 75, 80, 85, 90, 95]

print("Evaluación por algoritmo y umbral:\n")
print(f"{'Algoritmo':<20} {'Umbral':<8} {'TP':<4} {'FP':<4} {'TN':<4} {'FN':<4} {'Precisión':<10} {'Recall':<10}")
print("-" * 70)

mejor_config = {"algoritmo": None, "umbral": None, "f1_score": 0}

for nombre_algo in ALGORITMOS.keys():
    for umbral in UMBRALES:
        df_algo = df[df["algoritmo"] == nombre_algo].copy()

        # Clasificar como "mismo jugador" si similitud >= umbral
        df_algo["prediccion"] = df_algo["similitud"] >= umbral

        # True Positives: Predijo "mismo" y SÍ era el mismo
        TP = len(df_algo[(df_algo["prediccion"] == True) & (df_algo["son_mismo_real"] == True)])

        # False Positives: Predijo "mismo" pero NO era el mismo
        FP = len(df_algo[(df_algo["prediccion"] == True) & (df_algo["son_mismo_real"] == False)])

        # True Negatives: Predijo "diferente" y SÍ era diferente
        TN = len(df_algo[(df_algo["prediccion"] == False) & (df_algo["son_mismo_real"] == False)])

        # False Negatives: Predijo "diferente" pero SÍ era el mismo
        FN = len(df_algo[(df_algo["prediccion"] == False) & (df_algo["son_mismo_real"] == True)])

        # Métricas
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        print(f"{nombre_algo:<20} {umbral:<8} {TP:<4} {FP:<4} {TN:<4} {FN:<4} {precision:< 10.2f} {recall:<10.2f}")

        # Guardar mejor configuración
        if f1_score > mejor_config["f1_score"]:
            mejor_config = {
                "algoritmo": nombre_algo,
                "umbral": umbral,
                "f1_score": f1_score,
                "precision": precision,
                "recall": recall,
                "TP": TP,
                "FP": FP,
                "TN": TN,
                "FN": FN,
            }

# ==============================================================================
# RECOMENDACIÓN FINAL
# ==============================================================================

print(f"\n{'='*70}")
print("🏆 MEJOR CONFIGURACIÓN")
print(f"{'='*70}\n")

print(f"🥇 Algoritmo: {mejor_config['algoritmo']}")
print(f"🎯 Umbral: {mejor_config['umbral']}%")
print(f"📊 F1-Score: {mejor_config['f1_score']:.2f}")
print(f"✅ Precisión: {mejor_config['precision']:.2f} (de los que dijo 'mismo', cuántos eran correctos)")
print(f"✅ Recall: {mejor_config['recall']:.2f} (de los que SÍ eran mismo, cuántos detectó)")
print(f"\nMatriz de confusión:")
print(f"   TP (Correctos positivos): {mejor_config['TP']}")
print(f"   FP (Falsos positivos): {mejor_config['FP']}")
print(f"   TN (Correctos negativos): {mejor_config['TN']}")
print(f"   FN (Falsos negativos): {mejor_config['FN']}")

# ==============================================================================
# CASOS PROBLEMÁTICOS
# ==============================================================================

print(f"\n{'='*70}")
print("⚠️  CASOS PROBLEMÁTICOS (revisar manualmente)")
print(f"{'='*70}\n")

df_mejor = df[df["algoritmo"] == mejor_config["algoritmo"]].copy()
df_mejor["prediccion"] = df_mejor["similitud"] >= mejor_config["umbral"]

# Casos mal clasificados
errores = df_mejor[df_mejor["prediccion"] != df_mejor["son_mismo_real"]]

if len(errores) > 0:
    print(f"Se encontraron {len(errores)} errores:\n")
    for _, row in errores.iterrows():
        tipo_error = "FALSE POSITIVE" if row["prediccion"] else "FALSE NEGATIVE"
        print(f"❌ {tipo_error}")
        print(f"   '{row['nombre1']}' ←→ '{row['nombre2']}'")
        print(f"   Similitud: {row['similitud']}% | Real: {row['son_mismo_real']} | Predicción: {row['prediccion']}")
        print()
else:
    print("✅ No se encontraron errores con esta configuración")

# ==============================================================================
# CONCLUSIÓN
# ==============================================================================

print(f"\n{'='*70}")
print("💡 CONCLUSIÓN Y PRÓXIMOS PASOS")
print(f"{'='*70}\n")

if mejor_config["f1_score"] >= 0.90:
    print("✅ EXCELENTE: El algoritmo funciona muy bien (F1 >= 0.90)")
    print(f"✅ Recomendación: Usar {mejor_config['algoritmo']} con umbral {mejor_config['umbral']}% en producción")
elif mejor_config["f1_score"] >= 0.75:
    print("⚠️  BUENO: El algoritmo funciona aceptablemente (F1 >= 0.75)")
    print(f"⚠️  Recomendación: Usar {mejor_config['algoritmo']} con umbral {mejor_config['umbral']}%")
    print("⚠️  Considerar revisar manualmente casos dudosos")
else:
    print("❌ REGULAR: El algoritmo necesita mejoras (F1 < 0.75)")
    print("❌ Recomendación: Ajustar dataset de prueba o usar información adicional")
    print("    (ej: edad, equipo, posición para desempatar)")

print(f"\n📝 Siguiente paso:")
print(f"   Ejecutar: python research/scrapers_test/05_fuzzy_matching_bd.py")
print(f"   Para aplicar el algoritmo a los 110 jugadores en PostgreSQL\n")
