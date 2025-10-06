# 🗂️ Sistema de Gestión de Licencias - Guía de Distribución Portable

## 📦 Cómo generar el paquete distribuible

### Requisitos previos
- Python 3.11.9 instalado en tu PC de desarrollo
- Proyecto funcionando correctamente con `run.bat`

### Paso 1: Descargar Python embebido

1. Descargá Python embebido (portable) desde:
   ```
   https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip
   ```

2. Creá la carpeta de distribución:
   ```cmd
   mkdir dist\LicenciasEscolares
   ```

3. Descomprimí el ZIP de Python dentro de:
   ```
   dist\LicenciasEscolares\python\
   ```

### Paso 2: Configurar Python embebido

1. Abrí el archivo `dist\LicenciasEscolares\python\python311._pth` con el Bloc de notas

2. Buscá la línea:
   ```
   #import site
   ```

3. Quitale el `#` para que quede:
   ```
   import site
   ```

4. Guardá y cerrá

### Paso 3: Instalar dependencias en Python portable

Abrí CMD en la carpeta del proyecto y ejecutá:

```cmd
cd dist\LicenciasEscolares

REM Descargar get-pip
python\python.exe -c "import urllib.request; urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')"

REM Instalar pip
python\python.exe get-pip.py

REM Instalar dependencias
python\python.exe -m pip install streamlit>=1.31.0 pandas>=2.2.3 sqlmodel>=0.0.25 openpyxl>=3.1.2 python-dateutil>=2.9.0

REM Borrar archivo temporal
del get-pip.py
```

### Paso 4: Copiar archivos de la aplicación

```cmd
REM Desde la raíz del proyecto
copy app.py dist\LicenciasEscolares\
copy INICIAR.bat dist\LicenciasEscolares\
```

### Paso 5: Crear el archivo INICIAR.bat

Creá (o verificá que existe) el archivo `dist\LicenciasEscolares\INICIAR.bat` con este contenido:

```batch
@echo off
title Licencias Escolares - Mendoza
color 0A

echo ========================================
echo Sistema de Gestion de Licencias
echo Secretaria Escolar - Mendoza
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
    echo [ERROR] Hubo un problema al iniciar la aplicacion
    pause
)
```

### Paso 6: Estructura final

La carpeta `dist\LicenciasEscolares\` debe tener esta estructura:

```
dist\LicenciasEscolares\
├── python\              (Python embebido completo)
│   ├── python.exe
│   ├── python311.dll
│   ├── python311._pth   (modificado)
│   ├── Lib\
│   └── ... (otros archivos)
├── app.py              (tu aplicación)
└── INICIAR.bat         (launcher)
```

### Paso 7: Probar localmente

Antes de distribuir, probá:

```cmd
cd dist\LicenciasEscolares
INICIAR.bat
```

Debe:
1. Abrir la ventana de CMD
2. Después de 5 segundos, abrir el navegador
3. Mostrar la aplicación funcionando

### Paso 8: Comprimir para distribución

1. Seleccioná estos 3 elementos dentro de `dist\LicenciasEscolares\`:
   - Carpeta `python`
   - Archivo `app.py`
   - Archivo `INICIAR.bat`

2. Clic derecho → "Enviar a" → "Carpeta comprimida"

3. Renombrá el ZIP: `LicenciasEscolares_v2.0.zip`

4. Tamaño aproximado: 80-100 MB

---

## 🔄 Actualizar a una nueva versión

### Si solo cambiaste el código (app.py)

1. Modificá `app.py` en tu proyecto
2. Copialo a `dist\LicenciasEscolares\`:
   ```cmd
   copy app.py dist\LicenciasEscolares\
   ```
3. Volvé a comprimir

### Si agregaste nuevas dependencias

1. Actualizá `requirements.txt` en tu proyecto

2. Instalá la nueva dependencia en el Python portable:
   ```cmd
   cd dist\LicenciasEscolares
   python\python.exe -m pip install nueva-libreria==version
   ```

3. Copiá el `app.py` actualizado:
   ```cmd
   copy ..\..\app.py .
   ```

4. Volvé a comprimir

### Si actualizaste Python

1. Borrá la carpeta `dist\LicenciasEscolares\`
2. Seguí todos los pasos desde el principio con la nueva versión de Python

---

## 📋 Cambios necesarios en los archivos del proyecto

### NO necesitás PyInstaller

**Eliminá o ignorá estos archivos:**
- `licencias.spec`
- `build_exe.bat`
- Carpetas `build\` y `dist\` generadas por PyInstaller

### Mantené estos archivos en el proyecto

```
licencias_mza/
├── app.py                      (código principal)
├── requirements.txt            (dependencias)
├── run.bat                     (para desarrollo local)
├── run.sh                      (para Linux/Mac)
├── README.md                   (documentación general)
├── README_DISTRIBUCION.md      (esta guía)
└── INICIAR.bat                 (template del launcher)
```

### Actualizá el .gitignore

Agregá estas líneas a `.gitignore`:

```
# PyInstaller (ya no se usa)
build/
dist/
*.spec

# Python portable (solo para distribución)
python/
get-pip.py

# Entorno virtual
.venv/
venv/

# Base de datos local
*.db

# Archivos temporales
__pycache__/
*.pyc
*.pyo
*.tmp
```

### Nuevo flujo de trabajo

**Para desarrollo:**
```cmd
run.bat
```

**Para generar distribución:**
```cmd
# Seguir los pasos de esta guía
# No usar PyInstaller
```

---

## 🚀 Instrucciones para usuarios finales

Incluí este texto en un archivo `INSTRUCCIONES_USUARIO.txt` dentro del ZIP:

```
==============================================
Sistema de Gestión de Licencias v2.0
Secretaría Escolar - Mendoza
==============================================

INSTALACIÓN:
1. Descomprimir el archivo ZIP en cualquier carpeta
2. NO necesita instalar nada adicional

USO:
1. Hacer doble clic en "INICIAR.bat"
2. Esperar a que se abra el navegador (5 segundos)
3. Si no se abre automáticamente, ir a: http://localhost:8501

CERRAR LA APLICACIÓN:
- Ir a la ventana negra (CMD)
- Presionar Ctrl+C
- Cerrar la ventana

UBICACIÓN DE LOS DATOS:
Los datos se guardan en:
C:\Users\[TuUsuario]\AppData\Local\LicenciasEscolares\licencias.db

BACKUP:
1. Presionar Windows + R
2. Escribir: %LOCALAPPDATA%\LicenciasEscolares
3. Copiar el archivo "licencias.db"

SOPORTE:
Web: nicomaure.com.ar
Desarrollador: Nicolas Maure
```

---

## ⚠️ Problemas comunes y soluciones

### "El puerto 8501 está en uso"
- Cerrá cualquier otra instancia de la aplicación
- Abrí el Administrador de tareas (Ctrl+Shift+Esc)
- Finalizá procesos "python.exe" o "cmd.exe" relacionados

### "No se abre el navegador"
- Abrí manualmente: http://localhost:8501
- Verificá que no haya un firewall bloqueando

### "Error al iniciar"
- Verificá que la carpeta `python` esté completa
- Verificá que `app.py` exista en la misma carpeta que `INICIAR.bat`

---

## 📊 Ventajas de este método vs PyInstaller

✅ **Funciona perfectamente** - Sin problemas de compatibilidad
✅ **Actualizaciones fáciles** - Solo reemplazás `app.py`
✅ **Más liviano** - ~80 MB vs ~200 MB de PyInstaller
✅ **Portable real** - No necesita instalación
✅ **Mejor rendimiento** - Python nativo, no empaquetado
✅ **Fácil de debugear** - Ves los errores en tiempo real

❌ PyInstaller con Streamlit tiene problemas conocidos de metadatos
❌ PyInstaller genera ejecutables más pesados
❌ PyInstaller es más lento de iniciar

---

## 🔖 Versionado

Cuando distribuyas nuevas versiones:

1. Cambiá el número de versión en `app.py`:
   ```python
   st.caption("🗂️ Sistema de Gestión de Licencias - Versión 2.1")
   ```

2. Nombrá el ZIP con la versión:
   ```
   LicenciasEscolares_v2.1.zip
   ```

3. Documentá los cambios en un archivo `CHANGELOG.txt`

---

**Desarrollado por Nicolas Maure | nicomaure.com.ar**