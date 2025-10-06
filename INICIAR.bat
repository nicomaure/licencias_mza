@echo off
title Licencias Escolares - Mendoza
color 0A

echo ========================================
echo Sistema de Gestion de Licencias
echo Secretaria Escolar - Mendoza
echo Version 2.0
echo ========================================
echo.
echo Iniciando aplicacion...
echo.
echo La aplicacion se abrira en tu navegador
echo en unos segundos...
echo.
echo Si no se abre automaticamente, accede a:
echo http://localhost:8501
echo.
echo Para CERRAR la aplicacion:
echo Presiona Ctrl+C en esta ventana
echo ========================================
echo.

cd /d "%~dp0"

REM Abrir el navegador despues de 5 segundos
start /min cmd /c "timeout /t 5 /nobreak && start http://localhost:8501"

REM Ejecutar streamlit
python\python.exe -m streamlit run app.py --server.headless=true --server.port=8501 --browser.gatherUsageStats=false

if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Hubo un problema al iniciar
    echo ========================================
    echo.
    echo Posibles causas:
    echo - El puerto 8501 esta en uso
    echo - Faltan archivos de la aplicacion
    echo - Python no esta configurado correctamente
    echo.
    echo Soluciones:
    echo 1. Cierra otras instancias de la aplicacion
    echo 2. Verifica que existan las carpetas "python" y el archivo "app.py"
    echo 3. Reinicia tu computadora e intenta nuevamente
    echo.
    pause
)