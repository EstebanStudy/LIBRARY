@echo off
echo ================================================
echo        INICIANDO FRONTEND LIBRARY
echo ================================================
echo.

echo Sirviendo frontend en http://localhost:5500
echo Abre en tu navegador: http://localhost:5500/login.html
echo.
echo Presiona Ctrl + C para detener

python -m http.server 5500 --directory frontend

pause