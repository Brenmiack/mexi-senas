"""PASO 3 - Entrenar el clasificador (Random Forest) y medir que tan bien funciona.

Lee todos los data/*.csv, entrena y guarda models/modelo.joblib.
Si hay 2 o mas personas en los datos, tambien prueba con una persona que el modelo NO vio
(esa es la cifra honesta; la de "muestras al azar" sale inflada porque los cuadros
consecutivos de un video se parecen muchisimo).
No necesita GPU: entrena en segundos con CPU.
"""
import argparse
import csv
import glob
import os
from collections import Counter

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


def cargar(patron):
    personas, etiquetas, filas = [], [], []
    for ruta in sorted(glob.glob(patron)):
        with open(ruta, newline="", encoding="utf-8") as f:
            lector = csv.reader(f)
            next(lector, None)
            for fila in lector:
                if len(fila) < 3:
                    continue
                personas.append(fila[0])
                etiquetas.append(fila[1])
                filas.append([float(v) for v in fila[2:]])
    return np.array(filas, dtype=np.float32), np.array(etiquetas), np.array(personas)


def nuevo_modelo():
    return RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", default="data/*.csv")
    ap.add_argument("--salida", default="models/modelo.joblib")
    args = ap.parse_args()

    X, y, personas = cargar(args.datos)
    if len(X) == 0:
        raise SystemExit("No encontre muestras. Corre primero 02_recolectar.py")
    conteo = Counter(y)
    print("Muestras por etiqueta:", dict(conteo))
    print("Muestras por persona: ", dict(Counter(personas)))
    if len(conteo) < 2:
        raise SystemExit("Necesitas al menos 2 etiquetas (por ejemplo 'sena' y 'otra').")
    if min(conteo.values()) < 30:
        print("AVISO: hay muy pocas muestras en alguna etiqueta (menos de 30). Graba mas.")

    os.makedirs(os.path.dirname(args.salida) or ".", exist_ok=True)

    # 1) Prueba con muestras al azar (optimista)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    modelo = nuevo_modelo().fit(X_tr, y_tr)
    pred = modelo.predict(X_te)
    print("\n== Prueba con muestras al azar (optimista) ==")
    print(f"Precision: {accuracy_score(y_te, pred):.1%}")
    print(classification_report(y_te, pred, zero_division=0))
    clases = list(modelo.classes_)
    matriz = confusion_matrix(y_te, pred, labels=clases)
    print("Matriz de confusion (filas = real, columnas = predicho):", clases)
    print(matriz)

    # 2) Prueba con una persona que el modelo no vio (la cifra honesta)
    unicas = sorted(set(personas))
    if len(unicas) >= 2:
        print("\n== Prueba dejando a una persona fuera (la cifra honesta) ==")
        for p in unicas:
            fuera = personas == p
            if len(set(y[~fuera])) < 2 or fuera.sum() == 0:
                continue
            m = nuevo_modelo().fit(X[~fuera], y[~fuera])
            print(f"  Probando con {p}: {accuracy_score(y[fuera], m.predict(X[fuera])):.1%}  ({fuera.sum()} muestras)")
    else:
        print("\n(Con datos de una sola persona no se puede hacer la prueba honesta. Sumen datos de mas gente.)")

    # 3) Modelo final con TODOS los datos
    final = nuevo_modelo().fit(X, y)
    joblib.dump({"modelo": final, "clases": list(final.classes_)}, args.salida)
    print(f"\nModelo guardado en {args.salida}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from sklearn.metrics import ConfusionMatrixDisplay
        fig, ax = plt.subplots(figsize=(5, 4))
        ConfusionMatrixDisplay(matriz, display_labels=clases).plot(ax=ax, cmap="Blues", colorbar=False)
        ax.set_title("Matriz de confusion (prueba al azar)")
        fig.tight_layout()
        ruta_png = os.path.join(os.path.dirname(args.salida) or ".", "matriz_confusion.png")
        fig.savefig(ruta_png, dpi=150)
        print(f"Grafica guardada en {ruta_png} (sirve para la presentacion)")
    except ImportError:
        print("(Instala matplotlib si quieres la grafica de la matriz de confusion)")


if __name__ == "__main__":
    main()
