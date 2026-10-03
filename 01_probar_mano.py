"""PASO 1 - Probar que MediaPipe ve tu mano.

Abre la webcam y dibuja los 21 puntos de la mano.
  s = guardar captura (captura_mano.png)   q = salir
Este es el avance del dia 1: una captura o un video corto de esto funcionando.
"""
import argparse
import time

import cv2

from common import abrir_fuente, crear_detector, detectar_mano, dibujar_mano, texto


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fuente", default="0", help="0 = webcam, o ruta de un video")
    ap.add_argument("--espejo", action="store_true", help="voltear la imagen como espejo")
    args = ap.parse_args()

    cap, _ = abrir_fuente(args.fuente)
    detector = crear_detector()
    anterior = time.time()

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if args.espejo:
            frame = cv2.flip(frame, 1)

        mano = detectar_mano(detector, frame)
        if mano:
            dibujar_mano(frame, mano)
            texto(frame, "Mano detectada", (20, 40), (0, 255, 0))
        else:
            texto(frame, "Sin mano", (20, 40), (0, 0, 255))

        ahora = time.time()
        texto(frame, f"{1 / max(ahora - anterior, 1e-6):.0f} FPS", (20, 80), (255, 255, 255), 0.7, 2)
        anterior = ahora

        cv2.imshow("Probar mano (s = captura, q = salir)", frame)
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord("q"):
            break
        if tecla == ord("s"):
            cv2.imwrite("captura_mano.png", frame)
            print("Captura guardada: captura_mano.png")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
