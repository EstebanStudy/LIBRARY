@echo off
setlocal enabledelayedexpansion

echo ================================================
echo        INICIANDO SISTEMA LIBRARY
echo ================================================
echo.

:: Obtener el directorio donde se encuentra este .bat
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [1/4] Limpiando archivos de caché...
:: Eliminar __pycache__ desde la raíz del proyecto y dentro de Backend
for /d /r . %%G in (__pycache__) do (
    if exist "%%G" rmdir /s /q "%%G" 2>nul
)

:: Limpieza adicional de archivos .pyc (por si acaso)
del /s /q *.pyc 2>nul

echo [2/4] Configurando entorno virtual del Backend...
if not exist "Backend\venv" (
    echo    Creando entorno virtual...
    python -m venv Backend\venv
)

echo    Activando entorno virtual...
call Backend\venv\Scripts\activate.bat

echo [3/4] Instalando/actualizando dependencias...
pip install -r Backend\requirements.txt --quiet

echo [4/4] Iniciando Backend (FastAPI)...
echo.
echo Backend corriendo en: http://127.0.0.1:8000
echo Documentación: http://127.0.0.1:8000/docs
echo.
echo ================================================
echo Presiona Ctrl + C para detener el servidor
echo ================================================
echo.

cd Backend
python main.py

pause
endlocal