"""Funciones compartidas por todos los scripts.

Idea central: MediaPipe detecta 21 puntos de la mano en cada cuadro de video.
Convertimos esos puntos en 63 numeros (x, y, z de cada punto) normalizados para que
no importe donde este la mano en la imagen ni que tan cerca este de la camara.
Ese vector de 63 numeros es lo que aprende el clasificador.
"""
import os
import sys

import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

NUM_PUNTOS = 21
NUM_CARACTERISTICAS = NUM_PUNTOS * 3


def ruta_recurso(relativa):
    """Ruta de un archivo del proyecto (por ejemplo el modelo) que funciona igual en Python y en el .exe.

    Dentro del .exe, PyInstaller descomprime los archivos en una carpeta temporal (sys._MEIPASS).
    Fuera del .exe, la ruta se toma desde la carpeta del proyecto, sin importar desde donde se ejecute.
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relativa)


def crear_detector():
    """Crea el detector de manos de MediaPipe, configurado para video y una sola mano.

    static_image_mode=False: entre cuadros sigue la mano ya encontrada (mas rapido que buscarla cada vez).
    min_detection_confidence: que tan seguro debe estar MediaPipe para decir "aqui hay una mano".
    min_tracking_confidence: por debajo de este valor deja de seguirla y la vuelve a buscar.
    """
    return mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )


def abrir_fuente(fuente):
    """Abre la webcam o un video. Devuelve (captura, es_video).

    fuente: '0' para la webcam (o '1', '2'... si hay varias camaras), o la ruta de un video
    (por ejemplo uno grabado con el celular).
    """
    es_camara = str(fuente).isdigit()
    cap = cv2.VideoCapture(int(fuente) if es_camara else fuente)
    if not cap.isOpened():
        if es_camara:
            raise SystemExit(
                "No pude abrir la camara. Posibles causas:\n"
                "  - Otro programa la esta usando (Zoom, Teams, Meet, la app Camara): cierralo.\n"
                "  - Windows no le da permiso: Configuracion > Privacidad y seguridad > Camara.\n"
                "  - La computadora no tiene camara, o hay varias: prueba con --fuente 1"
            )
        raise SystemExit(f"No pude abrir el video: {fuente}\nRevisa que la ruta y el nombre del archivo sean correctos.")
    return cap, not es_camara


def ventana_cerrada(nombre):
    """True si el usuario cerro la ventana con la X.

    Sin esta revision, OpenCV vuelve a abrir la ventana en el siguiente cuadro y parece que no se puede cerrar.
    """
    return cv2.getWindowProperty(nombre, cv2.WND_PROP_VISIBLE) < 1


def detectar_mano(detector, frame_bgr):
    """Devuelve los 21 puntos de la mano o None si no hay mano en el cuadro."""
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    resultado = detector.process(rgb)
    if resultado.multi_hand_landmarks:
        return resultado.multi_hand_landmarks[0]
    return None


def a_caracteristicas(mano, ancho, alto):
    """21 puntos -> vector de 63 numeros normalizado.

    1) Pasamos a pixeles (para no deformar la mano por la forma de la imagen).
    2) Ponemos la muneca en el origen (da igual donde este la mano).
    3) Dividimos entre la distancia muneca -> base del dedo medio (da igual el tamano).
    """
    pts = np.array([[p.x * ancho, p.y * alto, p.z * ancho] for p in mano.landmark], dtype=np.float32)
    pts -= pts[0]
    escala = float(np.linalg.norm(pts[9]))
    if escala < 1e-6:
        escala = 1.0
    pts /= escala
    return pts.flatten()


def dibujar_mano(frame, mano):
    """Dibuja sobre el cuadro los 21 puntos de la mano y las lineas que los unen (modifica el cuadro)."""
    mp_draw.draw_landmarks(frame, mano, mp_hands.HAND_CONNECTIONS)


def texto(frame, contenido, posicion, color=(255, 255, 0), escala=1.0, grosor=2):
    """Texto sin acentos (las fuentes de OpenCV no los dibujan)."""
    cv2.putText(frame, contenido, posicion, cv2.FONT_HERSHEY_SIMPLEX, escala, (0, 0, 0), grosor + 3, cv2.LINE_AA)
    cv2.putText(frame, contenido, posicion, cv2.FONT_HERSHEY_SIMPLEX, escala, color, grosor, cv2.LINE_AA)
