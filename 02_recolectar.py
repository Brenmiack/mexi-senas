"""PASO 2 - Recolectar muestras.

(este script es el paso dos del proyecto)
Sirve para crear el dataset con el que se entrenara el modelo de datos...
Cada cuadro donde se ve la mano se guarda como una fila en data/<persona>.csv
(solo numeros de los puntos, NO se guardan fotos ni rostros).

Con solo UNA seña necesitas DOS etiquetas:
  --etiqueta L      la seña que quieren reconocer (el nombre que quieran)
  --etiqueta otra   cualquier otra cosa: mano abierta, puno, otras senas, mano en reposo...
Sin la etiqueta "otra" el modelo diria "es la seña" siempre, el poner la etiqueta otra permite tambien indentificar 
todo lo que NO es una de las 5 letras: mano abierta, puño, mano relajada, índice solo, pulgar arriba, OK.
Si el modelo solo hubiera visto letras, a cualquier mano le asignaría la letra más parecida.

Teclas (webcam):  ESPACIO = cuenta regresiva y grabar / pausar   q = salir
"""
import argparse #Permite pasar opciones desde terminal
import csv      #para archivos csv (escribir filas en el archivo de las pruebas)
import math     #se usa para math.ceil en la cuenta regresiva
import os       #maneja rutas y carpetas
import time     #medir segundos, especificamente en cuenta regresiva

import cv2      #leer camara, mostrar ventanas y guardar videos, en si habilita OpenCV

from common import (NUM_CARACTERISTICAS, a_caracteristicas, abrir_fuente, crear_detector, detectar_mano,
                    dibujar_mano, texto, ventana_cerrada) #Importa herramientas de otro archivo del proyecto

#NUM_CARACTERISTICAS	        Cantidad de números por muestra (63)
#abrir_fuente(fuente)	        Abre webcam o video; devuelve (cap, es_video)
#crear_detector()	            Crea el detector de manos
#detectar_mano(detector, frame)	Devuelve los puntos de la mano, o None si no hay
#a_caracteristicas(mano, ancho, alto)	Convierte los puntos en la lista de 63 números
#dibujar_mano(frame, mano)	    Dibuja el esqueleto sobre la imagen
#texto(...)	                    Escribe texto sobre la imagen
#ventana_cerrada(nombre)	    Revisa si el usuario cerró la ventana con la X
VENTANA = "Recolectar muestras"
SEGUNDOS_CUENTA = 3
FPS_VIDEO = 20

class VideoEvidencia:
  #Guarda en un .mp4 lo que se graba (eviencia del proceso)
  #La deteccion de mano no siempre es a la misma velocidad asi que cada cuadro se escribe las veces necesarias
    def __init__(self, ruta):
        """Prepara el video; el archivo se crea hasta el primer cuadro, cuando ya se conoce su tamano."""
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
    """
    Argumentos de línea de comandos:

    Argumento	    Para qué sirve o como sirve
    --persona	    Quién graba (permite luego evaluar con personas que el modelo no vio)
    --etiqueta	    Nombre de la clase (literal la etiqueta): L, otra, etc.
    --fuente	    0 = webcam, o ruta a un video
    --salida	    CSV de destino (por defecto data/<persona>.csv)
    --max	        Máximo de muestras por corrida (400 tomas)
    --cada	        Guarda 1 de cada N cuadros (2), para evitar muestras casi idénticas
    --sin-espejo	Desactiva el volteo horizontal de la imagen  aplicado para el programa y que identifique señas de manera de espejo
    --sin-video	    No guarda el video de evidencia
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
