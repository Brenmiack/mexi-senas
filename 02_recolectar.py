"""PASO 2 - Recolectar muestras.

Cada cuadro donde se ve la mano se guarda como una fila en data/muestras.csv
(solo numeros de los puntos, NO se guardan fotos ni rostros).

Con solo UNA sena necesitas DOS etiquetas:
  --etiqueta sena   la sena que quieren reconocer
  --etiqueta otra   cualquier otra cosa: mano abierta, puno, otras senas, mano en reposo...
Sin la etiqueta "otra" el modelo diria "es la sena" siempre.

Ejemplos:
  python 02_recolectar.py --persona ana --etiqueta sena
  python 02_recolectar.py --persona ana --etiqueta otra
  python 02_recolectar.py --persona luis --etiqueta sena --fuente video_celular.mp4   (sin ventana, automatico)

Teclas (webcam):  ESPACIO = empezar/pausar la grabacion   q = salir
Tips: cambia un poco la distancia, el angulo, la luz y el fondo mientras grabas.
"""
import argparse
import csv
import os

import cv2

from common import (NUM_CARACTERISTICAS, a_caracteristicas, abrir_fuente, crear_detector, detectar_mano,
                    dibujar_mano, texto)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--persona", required=True, help="quien graba (sirve para evaluar con gente que el modelo no vio)")
    ap.add_argument("--etiqueta", required=True, help="por ejemplo: sena  u  otra")
    ap.add_argument("--fuente", default="0", help="0 = webcam, o ruta de un video")
    ap.add_argument("--salida", default="data/muestras.csv")
    ap.add_argument("--max", type=int, default=400, help="maximo de muestras en esta corrida")
    ap.add_argument("--cada", type=int, default=2, help="guardar 1 de cada N cuadros (menos duplicados)")
    ap.add_argument("--espejo", action="store_true")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.salida) or ".", exist_ok=True)
    nuevo = not os.path.exists(args.salida)
    archivo = open(args.salida, "a", newline="", encoding="utf-8")
    escritor = csv.writer(archivo)
    if nuevo:
        escritor.writerow(["persona", "etiqueta"] + [f"f{i}" for i in range(NUM_CARACTERISTICAS)])

    cap, es_video = abrir_fuente(args.fuente)
    detector = crear_detector()
    grabando = es_video  # un video se procesa solo; la webcam espera a que pulses ESPACIO
    guardadas = 0
    cuadro = 0

    while guardadas < args.max:
        ok, frame = cap.read()
        if not ok:
            break
        if args.espejo:
            frame = cv2.flip(frame, 1)
        cuadro += 1

        mano = detectar_mano(detector, frame)
        if mano and grabando and cuadro % args.cada == 0:
            alto, ancho = frame.shape[:2]
            escritor.writerow([args.persona, args.etiqueta] + [f"{v:.5f}" for v in a_caracteristicas(mano, ancho, alto)])
            guardadas += 1

        if not es_video:
            if mano:
                dibujar_mano(frame, mano)
            estado = "GRABANDO" if grabando else "PAUSA (ESPACIO para grabar)"
            texto(frame, f"{args.etiqueta} | {estado}", (20, 40), (0, 0, 255) if grabando else (0, 255, 255), 0.8)
            texto(frame, f"muestras: {guardadas}/{args.max}", (20, 80), (255, 255, 255), 0.8)
            cv2.imshow("Recolectar (ESPACIO = grabar/pausar, q = salir)", frame)
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord("q"):
                break
            if tecla == 32:
                grabando = not grabando

    archivo.close()
    cap.release()
    cv2.destroyAllWindows()
    print(f"Listo: {guardadas} muestras de '{args.etiqueta}' guardadas en {args.salida}")


if __name__ == "__main__":
    main()
