# Reconocedor de una seña con visión artificial

Sprint IA · Rama: visión artificial. Meta: que la webcam reconozca **una seña** en vivo (y más si sobra tiempo).

Cómo funciona: MediaPipe saca 21 puntos de la mano en cada cuadro → los convertimos en 63 números
→ un clasificador (Random Forest) decide si es la seña o no. **No necesita GPU**: todo corre en CPU.

## Arranque (10 minutos, cada integrante que tenga laptop)

Necesitas Python 3.11 (3.10 o 3.12 también sirven; evita 3.13) y una webcam.

```bash
# Windows
py -3.11 -m venv .venv
.venv\Scripts\activate
# Mac / Linux
python3.11 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python 01_probar_mano.py
```

Si ves tu mano con los puntos dibujados, el entorno quedó listo. Importante: usen las versiones
de `requirements.txt` (mediapipe 0.10.14). Las versiones nuevas de mediapipe cambiaron la API y este código no corre con ellas.

## Los 4 pasos

| Paso | Script | Para qué |
|---|---|---|
| 1 | `01_probar_mano.py` | Comprobar que la cámara y MediaPipe funcionan (`s` guarda captura) |
| 2 | `02_recolectar.py` | Grabar muestras (ESPACIO empieza/pausa, `q` sale) |
| 3 | `03_entrenar.py` | Entrenar y medir precisión, guarda `models/modelo.joblib` y la matriz de confusión |
| 4 | `04_demo.py` | Demo en vivo (`--grabar demo.mp4` para el video de entrega) |

## Con una sola seña necesitas DOS etiquetas

```bash
python 02_recolectar.py --persona ana --etiqueta sena    # la seña elegida
python 02_recolectar.py --persona ana --etiqueta otra    # todo lo demás: mano abierta, puño, otras señas, mano en reposo
```

Sin ejemplos de `otra`, el modelo diría "es la seña" con cualquier mano. Graben más o menos la misma
cantidad de cada una (300–400 muestras por persona y etiqueta es un buen punto de partida).

Quien no pueda correr Python puede grabarse con el celular y pasar el video al que sí:
`python 02_recolectar.py --persona luis --etiqueta sena --fuente video.mp4` (se procesa solo, sin ventana).
Los CSV solo guardan números de puntos, no fotos ni rostros, así que se pueden subir al repositorio.

Reglas para que los datos sirvan:
- Todos usan la misma mano (recomendado la derecha) y la misma configuración de espejo (`--espejo` o ninguna) en grabar y en demo.
- Varíen distancia, ángulo, luz y fondo mientras graban. Un modelo entrenado con una sola persona y una sola luz falla con otra.
- Escriban en `--persona` su nombre de verdad: `03_entrenar.py` lo usa para probar con alguien que el modelo no vio.

## Plan de 8 días (miércoles 30 sep → miércoles 7 oct)

| Día | Meta | Avance que se le entrega al profesor |
|---|---|---|
| Mié 30 | Entorno funcionando, seña elegida, repositorio creado | Captura de la mano detectada + seña elegida + reparto de roles |
| Jue 1 | Primer lote de datos (todos graban) | Cantidad de muestras y ejemplos de variedad (personas, luz) |
| Vie 2 | Primer modelo entrenado | Precisión y matriz de confusión |
| Sáb 3 | Demo en vivo funcionando | Video corto de la demo |
| Dom 4 | Mejorar: más datos de `otra`, casos que fallan | Lista de errores y qué se corrigió |
| Lun 5 | Si va bien, segunda seña; si no, pulir la primera | Precisión antes y después |
| Mar 6 | Pruebas finales con gente nueva, video final, presentación | Ensayo de la presentación |
| Mié 7 | Entrega | Proyecto terminado |

Regla para decidir la segunda seña: solo si el sábado la demo ya funciona bien con personas que no grabaron datos.
Elijan una seña que se vea muy distinta de la primera (otra forma de mano, no una variación).

## Roles (5 integrantes)

1. **Líder técnico**: repositorio, revisa que todo corra, integra y prepara la demo final.
2. **Modelo**: corre `03_entrenar.py`, interpreta métricas, prueba cambios (más datos, umbral).
3. **Datos**: coordina quién graba qué, cuida la variedad y que haya suficientes ejemplos de `otra`.
4. **Pruebas**: prueba la demo con distintas personas y luces, anota cada error en una tabla (qué pasó, cuándo, con quién).
5. **Documentación y avances**: avance diario al profesor, bitácora de IA (obligatoria en la ficha), README y presentación.

Todos graban datos. Los dos con laptop potente pueden ser Líder y Modelo, pero no se necesita GPU: cualquier laptop con webcam sirve para grabar y probar.

## Elegir la seña

Elijan una seña **estática** (sin movimiento), con la mano bien visible y que se distinga de una mano abierta o un puño.
Verifiquen cómo se hace en una fuente de Lengua de Señas Mexicana (por ejemplo el diccionario DIELSEME) o con alguien de la comunidad sorda,
y anoten la fuente en el avance. Las señas con movimiento quedan fuera: este método analiza un solo cuadro.
