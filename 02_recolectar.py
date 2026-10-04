"""PASO 2 - Recolectar muestras.

Cada cuadro donde se ve la mano se guarda como una fila en data/<persona>.csv
(solo numeros de los puntos, NO se guardan fotos ni rostros).
Cada persona tiene su propio archivo para que no choquen al subirlos a git.

Con solo UNA sena necesitas DOS etiquetas:
  --etiqueta L      la sena que quieren reconocer (el nombre que quieran)
  --etiqueta otra   cualquier otra cosa: mano abierta, puno, otras senas, mano en reposo...
Sin la etiqueta "otra" el modelo diria "es la sena" siempre.

Ejemplos:
  python 02_recolectar.py --persona ana --etiqueta L
  python 02_recolectar.py --persona ana --etiqueta otra
  python 02_recolectar.py --persona luis --etiqueta L --fuente video_celular.mp4   (sin ventana, automatico)

Teclas (webcam):  ESPACIO = cuenta regresiva y grabar / pausar   q = salir
Con webcam tambien se guarda un video de evidencia en evidencia/ (--sin-video para no guardarlo).
Tips: cambia un poco la distancia, el angulo, la luz y el fondo mientras grabas.
"""
import argparse
import csv
import math
import os
import time

import cv2

from common import (NUM_CARACTERISTICAS, a_caracteristicas, abrir_fuente, crear_detector, detectar_mano,
                    dibujar_mano, texto, ventana_cerrada)

VENTANA = "Recolectar muestras"
SEGUNDOS_CUENTA = 3
FPS_VIDEO = 20


class VideoEvidencia:
    """Guarda en un .mp4 lo que se ve en la ventana mientras se graba (evidencia del proceso).

    La deteccion de la mano no siempre corre a la misma velocidad, asi que cada cuadro se escribe
    las veces necesarias para que el video dure lo mismo que la grabacion real.
    """

    def __init__(self, ruta):
        self.ruta = ruta
        self.escritor = None
        self.siguiente = None

    def escribir(self, frame):
        """Agrega el cuadro al video (lo crea con el tamano del primer cuadro)."""
        ahora = time.time()
        if self.escritor is None:
            alto, ancho = frame.shape[:2]
            self.escritor = cv2.VideoWriter(self.ruta, cv2.VideoWriter_fourcc(*"mp4v"), FPS_VIDEO, (ancho, alto))
            self.siguiente = ahora
        while self.siguiente <= ahora:
            self.escritor.write(frame)
            self.siguiente += 1 / FPS_VIDEO

    def cerrar(self):
        """Termina el archivo de video. Devuelve la ruta, o None si no se escribio nada."""
        if self.escritor is None:
            return None
        self.escritor.release()
        return self.ruta


def main():
    """Graba muestras de una etiqueta para una persona y las agrega a su CSV.

    Cada fila del CSV es: persona, etiqueta, y los 63 numeros de a_caracteristicas().
    Si el archivo ya existe, las filas nuevas se agregan al final (no se borra lo anterior).
    Con webcam, al presionar ESPACIO hay una cuenta regresiva para acomodar la mano antes de grabar.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--persona", required=True, help="quien graba (sirve para evaluar con gente que el modelo no vio)")
    ap.add_argument("--etiqueta", required=True, help="por ejemplo: L  u  otra")
    ap.add_argument("--fuente", default="0", help="0 = webcam, o ruta de un video")
    ap.add_argument("--salida", default=None, help="archivo CSV (por defecto data/<persona>.csv)")
    ap.add_argument("--max", type=int, default=400, help="maximo de muestras en esta corrida")
    ap.add_argument("--cada", type=int, default=2, help="guardar 1 de cada N cuadros (menos duplicados)")
    ap.add_argument("--sin-espejo", dest="espejo", action="store_false", help="no voltear la imagen")
    ap.add_argument("--sin-video", dest="video", action="store_false",
                    help="no guardar el video de evidencia en evidencia/ (solo aplica con webcam)")
    args = ap.parse_args()

    # "Ana Lopez" y "ana lopez" deben contar como la misma persona en 03_entrenar.py
    persona = args.persona.strip().lower().replace(" ", "_")
    salida = args.salida or os.path.join("data", f"{persona}.csv")

    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    nuevo = not os.path.exists(salida)
    archivo = open(salida, "a", newline="", encoding="utf-8")
    escritor = csv.writer(archivo)
    if nuevo:
        escritor.writerow(["persona", "etiqueta"] + [f"f{i}" for i in range(NUM_CARACTERISTICAS)])

    cap, es_video = abrir_fuente(args.fuente)
    detector = crear_detector()
    grabando = es_video  # un video se procesa solo; la webcam espera a que pulses ESPACIO
    fin_cuenta = None    # momento en que termina la cuenta regresiva (None = no hay cuenta en curso)
    guardadas = 0
    cuadro = 0
    evidencia = None
    if args.video and not es_video:
        os.makedirs("evidencia", exist_ok=True)
        etiqueta_archivo = "".join(c if c.isalnum() else "_" for c in args.etiqueta)
        evidencia = VideoEvidencia(os.path.join("evidencia", f"{persona}_{etiqueta_archivo}_{time.strftime('%H%M%S')}.mp4"))

    while guardadas < args.max:
        ok, frame = cap.read()
        if not ok:
            break
        if args.espejo:
            frame = cv2.flip(frame, 1)
        cuadro += 1
        alto, ancho = frame.shape[:2]

        if fin_cuenta is not None and time.time() >= fin_cuenta:
            fin_cuenta = None
            grabando = True

        mano = detectar_mano(detector, frame)
        if mano and grabando and cuadro % args.cada == 0:
            escritor.writerow([persona, args.etiqueta] + [f"{v:.5f}" for v in a_caracteristicas(mano, ancho, alto)])
            guardadas += 1

        if not es_video:
            if mano:
                dibujar_mano(frame, mano)
            if grabando:
                estado, color = "GRABANDO", (0, 0, 255)
            elif fin_cuenta is not None:
                estado, color = "PREPARATE...", (0, 255, 255)
                restante = max(1, math.ceil(fin_cuenta - time.time()))  # sin "0": al llegar ahi ya graba
                texto(frame, str(restante), (ancho // 2 - 40, alto // 2 + 40), (0, 255, 255), 4.0, 8)
            else:
                estado, color = "PAUSA (ESPACIO para grabar)", (0, 255, 255)
            texto(frame, f"{args.etiqueta} | {estado}", (20, 40), color, 0.8)
            texto(frame, f"muestras: {guardadas}/{args.max}", (20, 80), (255, 255, 255), 0.8)
            texto(frame, "ESPACIO = grabar/pausar    q = salir", (20, alto - 20), (255, 255, 255), 0.6, 1)
            if evidencia:
                evidencia.escribir(frame)
            cv2.imshow(VENTANA, frame)
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord("q") or ventana_cerrada(VENTANA):
                break
            if tecla == 32:  # ESPACIO
                if grabando or fin_cuenta is not None:
                    grabando, fin_cuenta = False, None  # pausar (o cancelar la cuenta) es inmediato
                else:
                    fin_cuenta = time.time() + SEGUNDOS_CUENTA

    archivo.close()
    cap.release()
    cv2.destroyAllWindows()
    print(f"Listo: {guardadas} muestras de '{args.etiqueta}' guardadas en {salida}")
    if evidencia and evidencia.cerrar():
        print(f"Video de evidencia: {evidencia.ruta}")


if __name__ == "__main__":
    main()
