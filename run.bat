@echo off
title Licencias Escolares - Mendoza
color 0A

echo ========================================
echo Sistema de Gestion de Licencias
echo Secretaria Escolar - Mendoza
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if exist .venv\Scripts\activate.bat (
    echo [OK] Entorno virtual encontrado
    call .venv\Scripts\activate.bat
) else (
    echo [INFO] Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual
        echo Verifica que Python este instalado correctamente
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
    echo [OK] Entorno virtual creado
    echo.
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas
)

echo.
echo ========================================
echo Iniciando aplicacion...
echo ========================================
echo.
echo La aplicacion se abrira automaticamente en tu navegador
echo.
echo Si no se abre, accede manualmente a:
echo http://localhost:8501
echo.
echo Para CERRAR la aplicacion: Presiona Ctrl+C en esta ventana
echo ========================================
echo.

streamlit run app.py --server.headless true --server.port 8501 --server.address localhost

if errorlevel 1 (
    echo.
    echo [ERROR] Hubo un problema al iniciar la aplicacion
    pause
)