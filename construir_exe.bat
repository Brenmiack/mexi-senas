@echo off
REM Genera la demo (04_demo.py) como programa de Windows, con el modelo entrenado adentro.
REM Quien lo abre no necesita instalar Python ni nada mas, solo tener webcam.
REM
REM Resultado:
REM   dist\ReconocedorSenas\ReconocedorSenas.exe   (el programa; necesita los archivos de su carpeta)
REM   dist\ReconocedorSenas.zip                    (la carpeta comprimida: esto se sube a GitHub Releases)
REM
REM Antes de correrlo:
REM   1) Instalar el entorno (ver README): .venv con requirements.txt
REM   2) Entrenar el modelo final:  python 03_entrenar.py
REM Cada vez que se re-entrene el modelo hay que volver a generar el .exe.

setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo No encuentro el entorno .venv. Sigue los pasos de instalacion del README.
    exit /b 1
)
if not exist "models\modelo.joblib" (
    echo Falta models\modelo.joblib. Primero entrena el modelo:  python 03_entrenar.py
    exit /b 1
)

REM --onedir                   carpeta en vez de un solo .exe: abre en ~4 s en vez de ~25 s cada vez
REM --collect-data mediapipe   copia los modelos internos de MediaPipe (detector de mano)
REM --hidden-import ...        el modelo guardado usa Random Forest de scikit-learn, pero
REM                            04_demo.py no lo importa directamente y PyInstaller no lo veria
REM --exclude-module jax ...   mediapipe instala jax pero este proyecto no lo usa (ahorra ~60 MB)
REM --add-data ...             mete el modelo dentro del programa (common.ruta_recurso lo encuentra)
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onedir ^
    --name ReconocedorSenas ^
    --collect-data mediapipe ^
    --hidden-import sklearn.ensemble._forest ^
    --exclude-module jax --exclude-module jaxlib ^
    --add-data "models\modelo.joblib;models" ^
    04_demo.py
if errorlevel 1 exit /b 1

echo Comprimiendo dist\ReconocedorSenas.zip ...
powershell -NoProfile -Command "Compress-Archive -Path 'dist\ReconocedorSenas' -DestinationPath 'dist\ReconocedorSenas.zip' -Force"
if errorlevel 1 exit /b 1

echo.
echo Listo: dist\ReconocedorSenas.zip
echo Pruebalo en una computadora SIN Python: descomprimir y abrir ReconocedorSenas.exe
echo (la primera vez tarda unos 25 segundos; despues unos 4).
