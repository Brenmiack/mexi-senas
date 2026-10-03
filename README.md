# Reconocedor de señas con visión artificial

Proyecto del curso *Explorando las ramas de la IA* · Rama: **visión artificial**.
La webcam reconoce en vivo una seña **estática** de Lengua de Señas Mexicana (LSM).

Cómo funciona: MediaPipe saca 21 puntos de la mano en cada cuadro de video → los convertimos en 63 números
→ un clasificador (Random Forest) decide qué seña es. **No necesita GPU**: todo corre en CPU.

## Usar el programa sin instalar nada (Windows)

1. Descargar `ReconocedorSenas.zip` de la sección **Releases** de este repositorio.
2. Descomprimirlo y abrir `ReconocedorSenas.exe` (la primera vez tarda unos 25 segundos en abrir).
3. Poner la mano frente a la cámara. Tecla `q` para salir.

## Instalación para desarrollar (Python)

Se necesita **Python 3.11** (3.10 y 3.12 también sirven). **No sirven 3.13 ni 3.14**: `mediapipe 0.10.14`
no se instala ahí, y las versiones nuevas de mediapipe cambiaron la API que usa este código.

```bash
# Windows
winget install Python.Python.3.11
py -3.11 -m venv .venv
.venv\Scripts\activate
# Mac / Linux
python3.11 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python 01_probar_mano.py
```

Si ves tu mano con los puntos dibujados, el entorno quedó listo. Cada vez que abras una terminal nueva,
activa el entorno (`.venv\Scripts\activate`) antes de correr los scripts.

## Los 4 pasos

| Paso | Script | Para qué |
|---|---|---|
| 1 | `01_probar_mano.py` | Comprobar que la cámara y MediaPipe funcionan (`s` guarda captura) |
| 2 | `02_recolectar.py` | Grabar muestras (ESPACIO: cuenta de 3 s y graba / pausa, `q` sale) |
| 3 | `03_entrenar.py` | Entrenar y medir precisión: guarda `models/modelo.joblib`, `models/metricas.txt` y las matrices de confusión |
| 4 | `04_demo.py` | Demo en vivo (`--grabar demo.mp4` para el video de entrega). Es lo mismo que el `.exe` |

Todos los scripts muestran la imagen **en espejo** (como un espejo normal). Si alguien usa `--sin-espejo`,
lo tienen que usar todos, al grabar y en la demo; si no, el modelo ve la mano al revés.

## Grabar datos

Cada persona graba su seña y también ejemplos de `otra` (todo lo que NO es la seña):

```bash
python 02_recolectar.py --persona ana --etiqueta L       # la seña elegida (el nombre que quieran)
python 02_recolectar.py --persona ana --etiqueta otra    # mano abierta, puño, mano en reposo, otras posiciones
```

- Cada persona queda en su propio archivo: `data/ana.csv`. Así no chocan al subirlos a git.
- Unas **300–400 muestras por persona y por etiqueta** (unos 30 segundos de grabación cada una).
  Graben más o menos la misma cantidad de la seña y de `otra`.
- No son fotos: cada muestra es un cuadro de video convertido en 63 números. Los CSV no guardan
  imágenes ni rostros, por eso se pueden subir al repositorio.
- Todos usan la misma mano (la derecha). Mientras graban, varíen distancia, ángulo, luz y fondo.
- Escriban en `--persona` su nombre de verdad: `03_entrenar.py` lo usa para probar el modelo con alguien que no vio.
- Quien grabe con el celular puede procesar el video así:
  `python 02_recolectar.py --persona luis --etiqueta L --fuente video.mp4`

## Generar el .exe

Con el entorno instalado y el modelo ya entrenado (`python 03_entrenar.py`), doble clic en
`construir_exe.bat` (o correrlo en la terminal). Deja `dist\ReconocedorSenas.zip`, que se sube a Releases.
Cada vez que se re-entrena el modelo hay que volver a generarlo.

## Estructura del repositorio

```
common.py               funciones compartidas: MediaPipe y la conversión de la mano a 63 números
01_probar_mano.py       paso 1
02_recolectar.py        paso 2
03_entrenar.py          paso 3
04_demo.py              paso 4 (también es el programa del .exe)
construir_exe.bat       genera el .exe
requirements.txt        librerías con su versión
data/                   muestras de cada integrante (datos de prueba)
models/                 modelo entrenado, metricas.txt y matrices de confusión
docs/QUE_HACER.md       qué le toca a cada integrante y cuándo
docs/guia_de_estudio.md preguntas y respuestas para la presentación tipo examen
docs/guion_video.md     guion del video demo
docs/entregables/       documentos para el profesor (01 a 05)
docs/bitacora_prompts.md
```

## Calendario

| Fecha | Meta |
|---|---|
| Vie 2 oct | Entorno, repositorio, seña elegida |
| Sáb 3 oct | Todos graban y suben su CSV; primer modelo |
| Dom 4 oct | Demo funcionando; cada quien documenta y modifica su archivo |
| Lun 5 oct | `.exe` probado en una PC sin Python; 01 y README completos |
| **Mar 6 oct** | **Entrega 1**: prototipo, repositorio, 01_Documento del proyecto |
| **Mié 7 oct** | **Entrega 2**: código documentado, 02_Manual del programador, 03_Informe QA |
| Jue 8 – Dom 11 | Manual de usuario, prueba con persona ajena, video |
| **Lun 12 oct** | **Entrega 3**: 04_Manual de usuario, 05_Nota de prueba, video demo |
| **Mar 13 oct** | **Entrega 4**: presentación y 06_Bitácora de prompts y reflexión |

## Equipo

| Rol | Integrante | Responsabilidad |
|---|---|---|
| Líder técnico | [nombre] | Repositorio, entrenar el modelo final, generar y probar el `.exe`, demo en vivo |
| Modelo | [nombre] | Interpretar métricas, experimentos de parámetros, video demo |
| Datos | [nombre] | Elegir la seña y su fuente, coordinar la grabación, manual de usuario |
| QA (pruebas) | [nombre] | Casos de prueba, informe QA, prueba con persona ajena |
| Documentación | [nombre] | Documento del proyecto, bitácora, presentación |

Qué tiene que hacer cada quien y cuándo: [docs/QUE_HACER.md](docs/QUE_HACER.md).
Para estudiar el proyecto: [docs/guia_de_estudio.md](docs/guia_de_estudio.md).

## Uso de IA

Registro completo de prompts: [docs/bitacora_prompts.md](docs/bitacora_prompts.md).

- **Código inicial** (`common.py`, los scripts 01–04, el primer README y `requirements.txt`; commit `5b48aec`):
  generado por Claude antes de empezar este registro. Su prompt (reconstruido, porque no se conservó
  el original) está en la fila 0 de la bitácora.
- **Generado por Claude** (Claude Code, modelo Opus 5.5, 2 oct 2026): todos los cambios al código inicial y los archivos nuevos.
  - Cada persona guarda sus muestras en `data/<persona>.csv`; el nombre se normaliza (minúsculas, sin espacios).
  - Imagen en espejo por defecto en todos los scripts (`--sin-espejo` para desactivarla).
  - Cuenta regresiva de 3 segundos antes de grabar; instrucciones de teclas dentro de las ventanas.
  - Las ventanas se pueden cerrar con la X (antes OpenCV las volvía a abrir).
  - Mensajes claros cuando la cámara no abre, falta el modelo o el video no existe; en el `.exe`, la consola
    espera a que se presione Enter para que se alcance a leer el error.
  - La demo muestra la probabilidad de la seña anunciada (antes podía mostrar la de otra clase).
  - La demo predice con un solo hilo (`n_jobs = 1`): ~8 ms por cuadro en vez de ~27 ms.
  - `03_entrenar.py` guarda `models/metricas.txt` y la matriz de confusión de la prueba con personas no vistas,
    e ignora filas dañadas de los CSV.
  - `common.ruta_recurso()` para que la demo encuentre el modelo dentro del `.exe`.
  - Docstrings de todas las funciones, `construir_exe.bat`, versiones fijas en `requirements.txt`,
    este README y los documentos de `docs/`.
- **Hecho por el equipo:** elección de la seña y su fuente, grabación de los datos (`data/*.csv`), entrenamiento
  del modelo final, pruebas con personas reales, prueba con persona ajena, video y presentación.
- **Modificado por el equipo** (llenar si cambian algo del código o de los documentos generados):

| Integrante | Archivo | Qué cambió |
|---|---|---|
| | | |

## Créditos y licencias

| Librería | Versión | Licencia | Enlace |
|---|---|---|---|
| MediaPipe (incluye el modelo de detección de manos *Hands*, de Google) | 0.10.14 | Apache 2.0 | https://github.com/google/mediapipe |
| OpenCV (`opencv-contrib-python`) | 4.11.0.86 | Apache 2.0 | https://opencv.org |
| NumPy | 1.26.4 | BSD-3-Clause | https://numpy.org |
| scikit-learn | 1.9.1 | BSD-3-Clause | https://scikit-learn.org |
| joblib | 1.6.0 | BSD-3-Clause | https://joblib.readthedocs.io |
| Matplotlib | 3.11.2 | Licencia de Matplotlib (basada en la PSF) | https://matplotlib.org |
| PyInstaller (solo para generar el `.exe`) | 6.22.3 | GPL-2.0 con excepción que permite distribuir el programa generado | https://pyinstaller.org |

- **Datos:** grabados por los integrantes del equipo con `02_recolectar.py`. No se usaron datasets externos.
- **Seña:** [nombre de la seña] según [fuente: por ejemplo el diccionario DIELSEME, con enlace].
- **Código:** ver "Uso de IA".

## Elegir la seña

Elijan una seña **estática** (sin movimiento), con la mano bien visible y que se distinga de una mano abierta o un puño.
Eviten letras con movimiento (J, Ñ, Z) y las que se parecen a una mano abierta o a un puño (A, B, E, S).
Buenas candidatas: L, V o Y. Verifiquen cómo se hace en una fuente de LSM (por ejemplo el diccionario DIELSEME)
o con alguien de la comunidad sorda, y anoten la fuente en el documento del proyecto.

Para agregar más señas no hay que cambiar código: se graba una etiqueta nueva y se re-entrena.
Háganlo solo si la demo ya funciona bien con personas que no grabaron datos, y elijan señas muy distintas entre sí.
