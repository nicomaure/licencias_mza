#!/bin/bash

echo "========================================"
echo "Sistema de Gestión de Licencias"
echo "Secretaría Escolar - Mendoza"
echo "========================================"
echo ""

# Verificar si existe el entorno virtual
if [ -d ".venv" ]; then
    echo "[OK] Entorno virtual encontrado"
    source .venv/bin/activate
else
    echo "[INFO] Creando entorno virtual..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudo crear el entorno virtual"
        echo "Verifica que Python esté instalado correctamente"
        read -p "Presiona Enter para salir..."
        exit 1
    fi
    source .venv/bin/activate
    echo "[OK] Entorno virtual creado"
    echo ""
    echo "[INFO] Instalando dependencias..."

    # Renombrar archivo si tiene espacio
    if [ -f "requirements.txt " ]; then
        mv "requirements.txt " requirements.txt
    fi

    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudieron instalar las dependencias"
        read -p "Presiona Enter para salir..."
        exit 1
    fi
    echo "[OK] Dependencias instaladas"
fi

echo ""
echo "========================================"
echo "Iniciando aplicación..."
echo "========================================"
echo ""
echo "La aplicación se abrirá automáticamente en tu navegador"
echo ""
echo "Si no se abre, accede manualmente a:"
echo "http://localhost:8501"
echo ""
echo "Para CERRAR la aplicación: Presiona Ctrl+C"
echo "========================================"
echo ""

streamlit run app.py --server.headless true --server.port 8501 --server.address localhost

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Hubo un problema al iniciar la aplicación"
    read -p "Presiona Enter para salir..."
fi