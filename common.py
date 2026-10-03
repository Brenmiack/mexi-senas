"""Funciones compartidas por todos los scripts.

Idea central: MediaPipe detecta 21 puntos de la mano en cada cuadro de video.
Convertimos esos puntos en 63 numeros (x, y, z de cada punto) normalizados para que
no importe donde este la mano en la imagen ni que tan cerca este de la camara.
Ese vector de 63 numeros es lo que aprende el clasificador.
"""
import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

NUM_PUNTOS = 21
NUM_CARACTERISTICAS = NUM_PUNTOS * 3


def crear_detector():
    return mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )


def abrir_fuente(fuente):
    """fuente: '0' para la webcam, o la ruta de un video (por ejemplo uno grabado con el celular)."""
    origen = int(fuente) if str(fuente).isdigit() else fuente
    cap = cv2.VideoCapture(origen)
    if not cap.isOpened():
        raise SystemExit(f"No pude abrir la fuente de video: {fuente}")
    return cap, not str(fuente).isdigit()


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
    mp_draw.draw_landmarks(frame, mano, mp_hands.HAND_CONNECTIONS)


def texto(frame, contenido, posicion, color=(255, 255, 0), escala=1.0, grosor=2):
    """Texto sin acentos (las fuentes de OpenCV no los dibujan)."""
    cv2.putText(frame, contenido, posicion, cv2.FONT_HERSHEY_SIMPLEX, escala, (0, 0, 0), grosor + 3, cv2.LINE_AA)
    cv2.putText(frame, contenido, posicion, cv2.FONT_HERSHEY_SIMPLEX, escala, color, grosor, cv2.LINE_AA)
