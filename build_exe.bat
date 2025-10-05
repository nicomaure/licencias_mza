@echo off
title Generar Ejecutable - Licencias Escolares
color 0B

echo ========================================
echo Generador de Ejecutable
echo Sistema de Licencias Escolares
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo [OK] Entorno virtual activado
) else (
    echo [ADVERTENCIA] No se encontro entorno virtual
    echo Asegurate de tener las dependencias instaladas
    echo.
)

echo.
echo [INFO] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
)
echo [OK] PyInstaller disponible

echo.
echo ========================================
echo Generando ejecutable...
echo Esto puede tardar varios minutos
echo ========================================
echo.

REM Limpiar builds anteriores
if exist build (
    echo [INFO] Limpiando build anterior...
    rmdir /s /q build
)
if exist dist (
    echo [INFO] Limpiando dist anterior...
    rmdir /s /q dist
)

REM Generar ejecutable
pyinstaller --clean licencias.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Fallo al generar el ejecutable
    echo ========================================
    echo.
    echo Posibles causas:
    echo - Faltan dependencias
    echo - Archivo licencias.spec incorrecto
    echo - Problemas de permisos
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [EXITO] Ejecutable generado correctamente
echo ========================================
echo.
echo Ubicacion: dist\LicenciasEscolares\
echo.
echo Para distribuir:
echo 1. Comprimir toda la carpeta "dist\LicenciasEscolares"
echo 2. Compartir el archivo .zip
echo 3. Los usuarios descomprimen y ejecutan LicenciasEscolares.exe
echo.
echo ========================================
pause