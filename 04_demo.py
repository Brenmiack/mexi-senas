"""PASO 4 - Demo en vivo: la camara ve la mano y dice que sena es.

  q = salir
Para grabar el video de la demo (entregable):  python 04_demo.py --grabar demo.mp4
"""
import argparse
from collections import Counter, deque

import cv2
import joblib

from common import a_caracteristicas, abrir_fuente, crear_detector, detectar_mano, dibujar_mano, texto


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="models/modelo.joblib")
    ap.add_argument("--fuente", default="0")
    ap.add_argument("--umbral", type=float, default=0.7, help="confianza minima para afirmar una sena")
    ap.add_argument("--negativa", default="otra", help="etiqueta que significa 'ninguna sena'")
    ap.add_argument("--grabar", default=None, help="guardar la demo en un video, por ejemplo demo.mp4")
    ap.add_argument("--espejo", action="store_true")
    ap.add_argument("--sin-ventana", action="store_true", help="no abrir ventana (para pruebas)")
    ap.add_argument("--max-cuadros", type=int, default=0, help="parar despues de N cuadros (0 = sin limite)")
    args = ap.parse_args()

    paquete = joblib.load(args.modelo)
    modelo, clases = paquete["modelo"], paquete["clases"]

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
                texto(frame, "Ninguna sena", (20, 50), (200, 200, 200), 1.2)
            else:
                texto(frame, f"Sena: {decision}  ({probas[mejor]:.0%})", (20, 50), (0, 255, 0), 1.2)

        if args.grabar:
            if escritor is None:
                escritor = cv2.VideoWriter(args.grabar, cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (ancho, alto))
            escritor.write(frame)

        if not args.sin_ventana:
            cv2.imshow("Demo (q = salir)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        if args.max_cuadros and cuadros >= args.max_cuadros:
            break

    if escritor:
        escritor.release()
        print(f"Video guardado en {args.grabar}")
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
