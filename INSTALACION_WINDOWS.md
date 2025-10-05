# 🪟 Guía de Instalación y Distribución - Windows 10/11

## ✅ Requisitos Previos

- **Windows 10 o Windows 11** (64 bits)
- **Python 3.8 o superior** instalado
  - Descargar desde: https://www.python.org/downloads/
  - ⚠️ **IMPORTANTE**: Durante la instalación, marcar ☑️ "Add Python to PATH"

## 🚀 Opción 1: Ejecutar directamente (Desarrollo)

### Pasos:

1. **Descargar o clonar el proyecto**
   ```bash
   git clone https://github.com/nicomaure/licencias_mza.git
   cd licencias_mza
   ```

2. **Ejecutar el archivo `run.bat`**
   - Hacer **doble clic** en `run.bat`
   - El script automáticamente:
     - ✅ Creará el entorno virtual (`.venv`)
     - ✅ Instalará todas las dependencias
     - ✅ Iniciará la aplicación en tu navegador

3. **La primera vez tardará más** (instalando dependencias)
   - Las siguientes veces se abrirá instantáneamente

### ⚙️ Lo que hace `run.bat` automáticamente:

```batch
# 1. Verifica si existe .venv, si no lo crea
python -m venv .venv

# 2. Activa el entorno virtual
.venv\Scripts\activate.bat

# 3. Instala las dependencias desde requirements.txt
pip install -r requirements.txt

# 4. Ejecuta la aplicación
streamlit run app.py
```

## 📦 Opción 2: Generar Ejecutable (.exe)

### Para distribuir la aplicación SIN necesidad de instalar Python:

### Pasos:

1. **Ejecutar `build_exe.bat`**
   - Hacer **doble clic** en `build_exe.bat`
   - El script automáticamente:
     - ✅ Instalará PyInstaller (si no está instalado)
     - ✅ Generará el ejecutable con todas las dependencias incluidas
     - ✅ Creará la carpeta `dist/LicenciasEscolares/`

2. **Tiempo de generación**
   - Primera vez: 5-10 minutos (dependiendo de tu PC)
   - Generará un ejecutable de aproximadamente **150-200 MB**

3. **Ubicación del ejecutable**
   ```
   dist/
   └── LicenciasEscolares/
       ├── LicenciasEscolares.exe  ← Ejecutable principal
       ├── _internal/               ← Librerías necesarias
       └── ... (otros archivos)
   ```

### 🎁 Distribuir el ejecutable:

1. **Comprimir toda la carpeta**
   ```
   Clic derecho en: dist\LicenciasEscolares\
   → Enviar a → Carpeta comprimida
   ```

2. **Compartir el archivo ZIP**
   - Enviar por email, Drive, WeTransfer, etc.

3. **Los usuarios solo deben:**
   - Descomprimir el ZIP
   - Ejecutar `LicenciasEscolares.exe`
   - ✅ **NO necesitan instalar Python ni dependencias**

## 🛠️ Dependencias que se instalarán automáticamente

El archivo `requirements.txt` incluye todas las dependencias necesarias:

```
streamlit>=1.31.0      # Framework web
pandas>=2.2.3          # Manejo de datos
sqlmodel>=0.0.14       # ORM para base de datos
openpyxl>=3.1.2        # Exportación a Excel
python-dateutil>=2.8.2 # Manejo de fechas
pyinstaller>=6.3.0     # Generador de ejecutables
```

### Compatibilidad:
- ✅ **Python 3.8** hasta **Python 3.13**
- ✅ **Windows 10** (64 bits)
- ✅ **Windows 11** (64 bits)
- ✅ Las versiones con `>=` permiten actualizaciones automáticas a versiones compatibles

## 🗄️ Base de Datos

### La base de datos se guarda automáticamente en:
```
C:\Users\[TuUsuario]\AppData\Local\LicenciasEscolares\licencias.db
```

### Ventajas:
- ✅ No requiere permisos de administrador
- ✅ Los datos persisten entre actualizaciones
- ✅ Fácil de respaldar y restaurar

### Hacer Backup:
```batch
# Método 1: Manual
1. Presionar Windows + R
2. Escribir: %LOCALAPPDATA%\LicenciasEscolares
3. Copiar el archivo: licencias.db

# Método 2: Comando
xcopy "%LOCALAPPDATA%\LicenciasEscolares\licencias.db" "C:\Backup\" /Y
```

## 🐛 Solución de Problemas Comunes

### 1. "Python no se reconoce como comando"
**Causa**: Python no está en el PATH

**Solución**:
1. Reinstalar Python
2. Marcar ☑️ "Add Python to PATH" durante la instalación
3. O agregar manualmente:
   - Panel de Control → Sistema → Configuración avanzada
   - Variables de entorno → Path → Editar
   - Agregar: `C:\Users\[Usuario]\AppData\Local\Programs\Python\Python3XX\`

### 2. "Error al instalar dependencias"
**Causa**: Problemas de red o permisos

**Solución**:
```batch
# Ejecutar como Administrador
1. Clic derecho en run.bat
2. "Ejecutar como administrador"

# O instalar manualmente
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Windows Defender bloquea el .exe
**Causa**: Falsa alarma de antivirus (común con PyInstaller)

**Solución**:
1. Clic en "Más información"
2. Clic en "Ejecutar de todas formas"
3. Es seguro: es tu propio ejecutable

### 4. Error "DLL not found" al ejecutar .exe
**Causa**: Faltan librerías de Visual C++

**Solución**:
- Descargar e instalar: **Microsoft Visual C++ Redistributable**
- Link: https://aka.ms/vs/17/release/vc_redist.x64.exe

### 5. El navegador no se abre automáticamente
**Causa**: Configuración del navegador predeterminado

**Solución**:
- Abrir manualmente: http://localhost:8501

## ✅ Verificación de Instalación Exitosa

### Después de ejecutar `run.bat`, deberías ver:

```
========================================
Sistema de Gestión de Licencias
Secretaría Escolar - Mendoza
========================================

[OK] Entorno virtual encontrado
[OK] Dependencias instaladas

========================================
Iniciando aplicación...
========================================

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.X.X:8501
```

### La aplicación se abre en el navegador mostrando:
- 🗂️ **Sistema de Gestión de Licencias - Secretaría Escolar Mendoza**
- Pestañas: ➕ Nueva licencia | 🔎 Listado / Gestión | ✏️ Editar / Eliminar | 📅 Reporte mensual
- Footer: **💻 Desarrollado por Nicolas Maure | nicomaure.com.ar**

## 📊 Tamaños Aproximados

| Componente | Tamaño |
|------------|--------|
| Proyecto fuente | ~50 KB |
| Entorno virtual (`.venv`) | ~300 MB |
| Ejecutable completo | ~200 MB |
| Base de datos (vacía) | ~20 KB |
| Base de datos (100 registros) | ~50 KB |

## 🔄 Actualizar el Proyecto

### Si descargas una nueva versión:

```batch
# Actualizar código
git pull origin main

# Actualizar dependencias (si cambiaron)
.venv\Scripts\activate
pip install -r requirements.txt --upgrade

# Los datos NO se pierden (están en AppData)
```

## 📞 Soporte

Si tienes problemas:
1. Revisar esta guía de solución de problemas
2. Abrir un [Issue en GitHub](https://github.com/nicomaure/licencias_mza/issues)
3. Contactar al desarrollador: [nicomaure.com.ar](https://nicomaure.com.ar)

---

<div align="center">

🗂️ **Sistema de Gestión de Licencias v2.0**

💻 Desarrollado por [Nicolas Maure](https://nicomaure.com.ar)

Secretaría Escolar - Mendoza, Argentina

</div>
