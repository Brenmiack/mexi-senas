# Reconocedor de señas con visión artificial

Proyecto del curso *Explorando las ramas de la IA* · Rama: **visión artificial**.
La webcam reconoce en vivo cinco letras **estáticas** del alfabeto de la Lengua de Señas Mexicana (LSM): L, Y, V, W y C.

Cómo funciona: MediaPipe saca 21 puntos de la mano en cada cuadro de video → los convertimos en 63 números
→ un clasificador (Random Forest) decide qué letra es (o «otra» si no es ninguna). **No necesita GPU**: todo corre en CPU.

## Usar el programa sin instalar nada (Windows)

1. Descargar `ReconocedorSenas.zip` de la sección **Releases** de este repositorio (https://github.com/Brenmiack/mexi-senas/releases).
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

Cada persona graba las 5 letras y también ejemplos de `otra` (todo lo que NO es una de las letras):

```bash
.venv\Scripts\python.exe 02_recolectar.py --persona ana --etiqueta L     # luego Y, V, W y C
.venv\Scripts\python.exe 02_recolectar.py --persona ana --etiqueta otra  # mano abierta, puño, relajada, índice solo, pulgar arriba, OK
```

- Cada persona queda en su propio archivo: `data/ana.csv`. Así no chocan al subirlos a git.
- Unas **300–400 muestras por persona y por etiqueta** (unos 30 segundos de grabación cada una).
  Graben la misma cantidad de cada letra y de `otra`.
- No son fotos: cada muestra es un cuadro de video convertido en 63 números. Los CSV no guardan
  imágenes ni rostros, por eso se pueden subir al repositorio.
- En `otra` no va ninguna de las 5 letras; la mano relajada, con los dedos estirados (si quedan curvos, parece una C).
- Con webcam se guarda también un video de evidencia en `evidencia/` (no se sube al repositorio).
- Todos usan la misma mano (la derecha): con la palma hacia la cámara, el pulgar de la L queda del lado izquierdo de la imagen. Mientras graban, varíen distancia, ángulo, luz y fondo.
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
pruebas/                datos del caso de prueba con la mano izquierda (no se usan para entrenar)
docs/bitacora_prompts.md  registro de los prompts usados con IA
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

## Equipo: MEXI-SEÑAS

| Rol | Integrante | Responsabilidad |
|---|---|---|
| Líder técnico | Paul Sahid Méndez Hernández | Repositorio, entrenar el modelo final, generar y probar el `.exe`, demo en vivo |
| Modelo | Oscar García Marroquín | Interpretar métricas, experimentos de parámetros, video demo |
| Datos | Daniela Díaz López | Elegir las letras y su fuente, coordinar la grabación, manual de usuario |
| QA (pruebas) | Leonardo González Cuevas | Casos de prueba, informe QA, prueba con persona ajena |
| Documentación | Kevin Zidam Valencia Vélez | Documento del proyecto, bitácora, presentación |

## Uso de IA

Registro completo de prompts: [docs/bitacora_prompts.md](docs/bitacora_prompts.md).

- **Código inicial** (`common.py`, los scripts 01–04, el primer README y `requirements.txt`; commit `5b48aec`):
  generado por Claude (claude.ai) el 30 de septiembre, a partir de la investigación inicial de Leonardo. Sus prompts
  originales están en las filas I-1 a I-10 y 0 a 0.3 de la bitácora.
- **Generado por Claude** (Claude Code, modelo Opus 5.5, 2 oct 2026): todos los cambios al código inicial y los archivos nuevos.
  - Cada persona guarda sus muestras en `data/<persona>.csv`; el nombre se normaliza (minúsculas, sin espacios).
  - Imagen en espejo por defecto en todos los scripts (`--sin-espejo` para desactivarla).
  - Cuenta regresiva de 3 segundos antes de grabar; instrucciones de teclas dentro de las ventanas;
    video de evidencia automático de cada grabación.
  - Las ventanas se pueden cerrar con la X (antes OpenCV las volvía a abrir).
  - Mensajes claros cuando la cámara no abre, falta el modelo o el video no existe; en el `.exe`, la consola
    espera a que se presione Enter para que se alcance a leer el error.
  - La demo muestra la probabilidad de la letra anunciada (antes podía mostrar la de otra clase).
  - La demo predice con un solo hilo (`n_jobs = 1`): ~8 ms por cuadro en vez de ~27 ms.
  - `03_entrenar.py` guarda `models/metricas.txt` y la matriz de confusión de la prueba con personas no vistas,
    e ignora filas dañadas de los CSV.
  - `common.ruta_recurso()` para que la demo encuentre el modelo dentro del `.exe`.
  - Docstrings de todas las funciones, `construir_exe.bat`, versiones fijas en `requirements.txt`,
    este README y los borradores de los documentos de entrega (01 a 06).
- **Hecho por el equipo:** elección de las letras y su fuente, grabación de los datos (`data/*.csv`), entrenamiento
  del modelo final, pruebas con personas reales, prueba con persona ajena, video y presentación.
- **Modificado por el equipo** (llenar si cambian algo del código o de los documentos generados):

| Integrante | Archivo | Qué cambió |
|---|---|---|
| Daniela Díaz López | `02_recolectar.py` | Descripción del script con sus palabras, comentarios en los `import` y tabla de argumentos en `main()` |
| Leonardo González Cuevas | `04_demo.py` | «sena» por «seña» en la descripción y los comentarios (los textos de la ventana siguen sin ñ porque OpenCV no la dibuja: ver ER-12) |

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
- **Señas:** letras L, Y, V, W y C del alfabeto manual de la LSM, según el DIELSEME, Diccionario Español–Lengua de Señas Mexicana (María Teresa Calvo Hernández, SEP, 2004; versión 2014): https://libreacceso.org/bibliografia/bibliografias-discapacidad-auditiva/dielseme-diccionario-espanol-lengua-de-senas-mexicana-sep/
- **Código:** ver "Uso de IA".

## Las señas elegidas

Se eligieron cinco letras **estáticas** y muy distintas entre sí: **L** (índice y pulgar extendidos), **Y** (pulgar y meñique), **V** (índice y medio separados), **W** (índice, medio y anular separados) y **C** (mano curva).
Se descartaron las letras con movimiento (J, K, Ñ, Q, X, Z), porque el programa analiza un cuadro a la vez, y las que se
parecen entre sí o a una mano abierta o un puño (A, B, E, M, N, S, T; U, R, H). Verifiquen cada letra en una fuente de LSM
(por ejemplo el diccionario DIELSEME) y anoten la fuente en el documento del proyecto.

Para agregar más letras no hay que cambiar código: se graba una etiqueta nueva y se re-entrena.
Revisen después en `models/metricas.txt` que la letra nueva no se confunda con las demás.

Resultados con los 5 integrantes (6 oct): 99.0 % con muestras al azar y **91.3 % con personas que el modelo no vio**
(de 83.0 % con Leonardo a 98.3 % con Paul; detalle en `models/metricas.txt`).
