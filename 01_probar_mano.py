"""PASO 1 - Probar que MediaPipe ve tu mano.

Abre la webcam y dibuja los 21 puntos de la mano.
  s = guardar captura (captura_mano.png)   q = salir (o cerrar la ventana)
Sirve para comprobar que la instalacion quedo bien antes de grabar datos.
"""


    Los FPS indican que tan fluido corre: por debajo de ~10 la demo en vivo se sentira lenta.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--fuente", default="0", help="0 = webcam, o ruta de un video")
    ap.add_argument("--sin-espejo", dest="espejo", action="store_false", help="no voltear la imagen")
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
        alto = frame.shape[0]

        mano = detectar_mano(detector, frame)
        if mano:
            dibujar_mano(frame, mano)
            texto(frame, "Mano detectada", (20, 40), (0, 255, 0))
        else:
            texto(frame, "Sin mano", (20, 40), (0, 0, 255))

        ahora = time.time()
        texto(frame, f"{1 / max(ahora - anterior, 1e-6):.0f} FPS", (20, 80), (255, 255, 255), 0.7, 2)
        anterior = ahora
        texto(frame, "s = guardar captura    q = salir", (20, alto - 20), (255, 255, 255), 0.6, 1)

        cv2.imshow(VENTANA, frame)
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord("q") or ventana_cerrada(VENTANA):
            break
        if tecla == ord("s"):
            cv2.imwrite("captura_mano.png", frame)
            print("Captura guardada: captura_mano.png")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
