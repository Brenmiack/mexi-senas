"""PASO 4 - Demo en vivo: la camara ve la mano y dice que seÑa es.

q = salir (o cerrar la ventana)
Para grabar el video de la demo (entregable):  python 04_demo.py --grabar demo.mp4
Este mismo script es el programa del .exe (ver construir_exe.bat).
"""
# Va antes de los imports porque cargar MediaPipe tarda: asi la ventana no parece colgada
print("Cargando el reconocedor de señas... (la primera vez puede tardar hasta 30 segundos)")

import argparse
import os
import sys
import traceback
from collections import Counter, deque

import cv2
import joblib

from common import (a_caracteristicas, abrir_fuente, crear_detector, detectar_mano, dibujar_mano, ruta_recurso,
                    texto, ventana_cerrada)

VENTANA = "Reconocedor de señas"

def main():
    """Abre la camara y en cada cuadro muestra que seña ve el modelo.

    Cada cuadro con mano se convierte en 63 numeros y el modelo da la probabilidad de cada etiqueta.
    Si la mas alta no llega al --umbral, el cuadro cuenta como "?" (incierto). Lo que se muestra
    es lo que mas se repite en los ultimos 5 cuadros (votacion), para que el texto no parpadee.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default=ruta_recurso("models/modelo.joblib"))
    ap.add_argument("--fuente", default="0", help="0 = webcam, o ruta de un video")
    ap.add_argument("--umbral", type=float, default=0.7, help="confianza minima para afirmar una seña")
    ap.add_argument("--negativa", default="otra", help="etiqueta que significa 'ninguna seña'")
    ap.add_argument("--grabar", default=None, help="guardar la demo en un video, por ejemplo demo.mp4")
    ap.add_argument("--sin-espejo", dest="espejo", action="store_false", help="no voltear la imagen")
    ap.add_argument("--sin-ventana", action="store_true", help="no abrir ventana (para pruebas)")
    ap.add_argument("--max-cuadros", type=int, default=0, help="parar despues de N cuadros (0 = sin limite)")
    args = ap.parse_args()

    if not os.path.exists(args.modelo):
        raise SystemExit(f"No encontre el modelo: {args.modelo}\n"
                         "Primero hay que entrenarlo con:  python 03_entrenar.py")
    paquete = joblib.load(args.modelo)
    modelo, clases = paquete["modelo"], paquete["clases"]
    modelo.n_jobs = 1  # se predice un cuadro a la vez: repartirlo en hilos lo hace ~3 veces mas lento

    cap, _ = abrir_fuente(args.fuente)
    detector = crear_detector()
    historial = deque(maxlen=5)  # votacion de los ultimos 5 cuadros: evita parpadeos
    escritor = None
    cuadros = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if args.espejo:
            frame = cv2.flip(frame, 1)
        cuadros += 1
        alto, ancho = frame.shape[:2]

        mano = detectar_mano(detector, frame)
        if mano is None:
            historial.clear()
            texto(frame, "Sin mano", (20, 50), (200, 200, 200), 1.2)
        else:
            dibujar_mano(frame, mano)
            probas = modelo.predict_proba([a_caracteristicas(mano, ancho, alto)])[0]
            mejor = int(probas.argmax())
            historial.append(clases[mejor] if probas[mejor] >= args.umbral else "?")
            decision = Counter(historial).most_common(1)[0][0]
            if decision == "?":
                texto(frame, "Incierto", (20, 50), (0, 255, 255), 1.2)
            elif decision == args.negativa:
                texto(frame, "Ninguna seña", (20, 50), (200, 200, 200), 1.2)
            else:
                # La probabilidad de la seña que se anuncia (no la de "mejor": en este cuadro puede ser otra)
                confianza = probas[clases.index(decision)]
                texto(frame, f"seña: {decision}  ({confianza:.0%})", (20, 50), (0, 255, 0), 1.2)
        texto(frame, "q = salir", (20, alto - 20), (255, 255, 255), 0.6, 1)

        if args.grabar:
            if escritor is None:
                escritor = cv2.VideoWriter(args.grabar, cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (ancho, alto))
            escritor.write(frame)

        if not args.sin_ventana:
            cv2.imshow(VENTANA, frame)
            if cv2.waitKey(1) & 0xFF == ord("q") or ventana_cerrada(VENTANA):
                break
        if args.max_cuadros and cuadros >= args.max_cuadros:
            break

    if escritor:
        escritor.release()
        print(f"Video guardado en {args.grabar}")
    cap.release()
    cv2.destroyAllWindows()


def esperar_si_es_exe():
    """En el .exe la ventana negra se cierra sola al terminar: esperar para que se alcance a leer el error."""
    if getattr(sys, "frozen", False):
        input("\nPresiona Enter para cerrar...")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as error:
        if isinstance(error.code, str):  # nuestros mensajes de error (sin modelo, sin camara...)
            print(error.code)
            esperar_si_es_exe()
            sys.exit(1)
        raise
    except Exception:
        traceback.print_exc()
        esperar_si_es_exe()
        sys.exit(1)
