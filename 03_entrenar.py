"""PASO 3 - Entrenar el clasificador (Random Forest) y medir que tan bien funciona.

Lee todos los data/*.csv, entrena y guarda models/modelo.joblib.
Si hay 2 o mas personas en los datos, tambien prueba con una persona que el modelo NO vio
(esa es la cifra honesta; la de "muestras al azar" sale inflada porque los cuadros
consecutivos de un video se parecen muchisimo).
Todo lo que imprime se guarda tambien en models/metricas.txt, junto con las graficas
de las matrices de confusion (sirven para los documentos y la presentacion).
No necesita GPU: entrena en segundos con CPU.
"""
import argparse
import csv
import glob
import os
from collections import Counter
from datetime import datetime

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from common import NUM_CARACTERISTICAS


def cargar(patron):
    """Lee todos los CSV que coinciden con el patron (por ejemplo data/*.csv).

    Devuelve (X, y, personas, descartadas):
      X: una fila de 63 numeros por muestra; y: la etiqueta de cada fila; personas: quien la grabo;
      descartadas: cuantas filas se ignoraron por estar incompletas o danadas.
    """
    personas, etiquetas, filas = [], [], []
    descartadas = 0
    for ruta in sorted(glob.glob(patron)):
        with open(ruta, newline="", encoding="utf-8") as f:
            lector = csv.reader(f)
            next(lector, None)  # encabezado
            for fila in lector:
                if len(fila) != 2 + NUM_CARACTERISTICAS:
                    descartadas += 1
                    continue
                try:
                    numeros = [float(v) for v in fila[2:]]
                except ValueError:
                    descartadas += 1
                    continue
                personas.append(fila[0])
                etiquetas.append(fila[1])
                filas.append(numeros)
    return np.array(filas, dtype=np.float32), np.array(etiquetas), np.array(personas), descartadas


def nuevo_modelo():
    """Crea un Random Forest sin entrenar.

    n_estimators: cuantos arboles votan (mas arboles = mas estable pero mas lento).
    random_state: fija el azar para que entrenar dos veces con los mismos datos de el mismo resultado.
    n_jobs=-1: entrena usando todos los nucleos del procesador.
    """
    return RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)


def guardar_matriz(matriz, clases, titulo, ruta_png):
    """Guarda la matriz de confusion como imagen PNG (filas = etiqueta real, columnas = lo que dijo el modelo)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(matriz, display_labels=clases).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(titulo)
    ax.set_xlabel("Lo que dijo el modelo")
    ax.set_ylabel("Etiqueta real")
    fig.tight_layout()
    fig.savefig(ruta_png, dpi=150)
    plt.close(fig)


def main():
    """Carga los datos, mide la precision de dos formas, entrena el modelo final y guarda resultados."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", default="data/*.csv")
    ap.add_argument("--salida", default="models/modelo.joblib")
    args = ap.parse_args()
    carpeta = os.path.dirname(args.salida) or "."

    lineas = [f"Entrenamiento: {datetime.now():%Y-%m-%d %H:%M}"]

    def reportar(contenido=""):
        """Imprime en pantalla y guarda la linea para models/metricas.txt."""
        print(contenido)
        lineas.append(str(contenido))

    X, y, personas, descartadas = cargar(args.datos)
    if descartadas:
        reportar(f"AVISO: se ignoraron {descartadas} filas incompletas o danadas en los CSV.")
    if len(X) == 0:
        raise SystemExit("No encontre muestras. Corre primero 02_recolectar.py")
    conteo = Counter(y)
    reportar(f"Muestras por etiqueta: {dict(conteo)}")
    reportar(f"Muestras por persona:  {dict(Counter(personas))}")
    if len(conteo) < 2:
        raise SystemExit("Necesitas al menos 2 etiquetas (por ejemplo 'L' y 'otra').")
    if min(conteo.values()) < 5:
        raise SystemExit("Hay una etiqueta con menos de 5 muestras: no alcanza para entrenar. Graba mas.")
    if min(conteo.values()) < 30:
        reportar("AVISO: hay muy pocas muestras en alguna etiqueta (menos de 30). Graba mas.")

    os.makedirs(carpeta, exist_ok=True)

    # 1) Prueba con muestras al azar (optimista)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    modelo = nuevo_modelo().fit(X_tr, y_tr)
    pred = modelo.predict(X_te)
    reportar("\n== Prueba con muestras al azar (optimista) ==")
    reportar(f"Precision: {accuracy_score(y_te, pred):.1%}")
    reportar(classification_report(y_te, pred, zero_division=0))
    clases = list(modelo.classes_)
    matriz = confusion_matrix(y_te, pred, labels=clases)
    reportar(f"Matriz de confusion (filas = real, columnas = predicho): {clases}")
    reportar(matriz)

    # 2) Prueba con una persona que el modelo no vio (la cifra honesta)
    unicas = sorted(set(personas))
    reales, predichas = [], []
    if len(unicas) >= 2:
        reportar("\n== Prueba dejando a una persona fuera (la cifra honesta) ==")
        for p in unicas:
            fuera = personas == p
            if len(set(y[~fuera])) < 2:
                continue
            m = nuevo_modelo().fit(X[~fuera], y[~fuera])
            pred_p = m.predict(X[fuera])
            reales.extend(y[fuera])
            predichas.extend(pred_p)
            reportar(f"  Probando con {p}: {accuracy_score(y[fuera], pred_p):.1%}  ({fuera.sum()} muestras)")
        if reales:
            reportar(f"  Total con personas no vistas: {accuracy_score(reales, predichas):.1%}")
            matriz_honesta = confusion_matrix(reales, predichas, labels=clases)
            reportar(f"Matriz de confusion (filas = real, columnas = predicho): {clases}")
            reportar(matriz_honesta)
    else:
        reportar("\n(Con datos de una sola persona no se puede hacer la prueba honesta. Sumen datos de mas gente.)")

    # 3) Modelo final con TODOS los datos
    final = nuevo_modelo().fit(X, y)
    joblib.dump({"modelo": final, "clases": list(final.classes_)}, args.salida)
    reportar(f"\nModelo guardado en {args.salida}")

    ruta_metricas = os.path.join(carpeta, "metricas.txt")
    with open(ruta_metricas, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"Metricas guardadas en {ruta_metricas}")

    try:
        guardar_matriz(matriz, clases, "Matriz de confusión (prueba al azar)",
                       os.path.join(carpeta, "matriz_confusion.png"))
        if reales:
            guardar_matriz(matriz_honesta, clases, "Matriz de confusión (personas no vistas)",
                           os.path.join(carpeta, "matriz_confusion_honesta.png"))
        print(f"Graficas guardadas en {carpeta} (sirven para la presentacion)")
    except ImportError:
        print("(Instala matplotlib si quieres las graficas de la matriz de confusion)")


if __name__ == "__main__":
    main()
