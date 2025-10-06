
# 🗂️ Sistema de Gestión de Licencias - Secreta### Opción B: Generar versión portable para Windows

Para distribuir la aplicación sin requerir instalación de Python:

1. **Seguir la guía completa:** Ver [README_DISTRIBUCION.md](README_DISTRIBUCION.md)

2. **Resumen rápido:**
   - Descargar Python embebido (portable)
   - Instalar dependencias en el Python portable
   - Comprimir y distribuir

3. **Ventajas:**
   - No requiere instalación de Python
   - Funciona en cualquier PC con Windows 10/11
   - Sin errores de importlib_metadata
   - Tamaño: ~80-100 MB comprimido

4. **Los usuarios solo:**
   - Descomprimen el ZIP
   - Ejecutan `INICIAR.bat`
   - ¡Listo!za

Sistema completo de gestión de licencias escolares para Mendoza, Argentina. Desarrollado con Python y Streamlit.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Características

✅ **Gestión completa de licencias**
- Alta, baja y modificación de licencias
- Búsqueda avanzada por múltiples criterios
- Exportación a CSV y Excel
- Reportes mensuales para impresión

✅ **Base de datos persistente**
- SQLite integrado
- Almacenamiento en AppData (sin problemas de permisos)
- Backup y restauración fácil

✅ **Interfaz intuitiva**
- Diseño moderno con Streamlit
- Responsive y fácil de usar
- Impresión optimizada con Ctrl+P

✅ **Distribución flexible**
- Ejecución directa con Python
- Generación de ejecutable (.exe) para Windows
- Sin dependencias externas en modo ejecutable

## 🚀 Inicio rápido

### Opción A: Ejecutar directamente (Recomendado para desarrollo)

1. **Clonar el repositorio:**
```bash
git clone https://github.com/nicomaure/licencias_mza.git
cd licencias_mza
```

2. **Ejecutar:**
   - **Windows:** Doble clic en `run.bat`
   - **Linux/Mac:** `bash run.sh`

3. La aplicación se abrirá automáticamente en tu navegador

### Opción B: Generar ejecutable (.exe)

1. **Generar el ejecutable:**
```bash
# Windows
build_exe.bat

# O manualmente:
pyinstaller --clean licencias.spec
```

2. **El ejecutable estará en:** `dist/LicenciasEscolares/`

3. **Distribuir:**
   - Comprimir toda la carpeta `dist/LicenciasEscolares/`
   - Compartir el archivo ZIP
   - Los usuarios descomprimen y ejecutan `LicenciasEscolares.exe`

## 📦 Instalación manual

Si prefieres instalar manualmente:

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```


## 🗄️ Ubicación de los datos

Los datos se guardan automáticamente en:

- **Windows:** `C:\Users\[Usuario]\AppData\Local\LicenciasEscolares\licencias.db`
- **Linux/Mac:** `~/.licencias_escolares/licencias.db`

### Hacer backup

**Windows:**
1. Presionar `Windows + R`
2. Escribir: `%LOCALAPPDATA%\LicenciasEscolares`
3. Copiar el archivo `licencias.db`

**Linux/Mac:**
```bash
cp ~/.licencias_escolares/licencias.db ~/backup_licencias.db
```

### Restaurar backup

1. Cerrar la aplicación
2. Ir a la carpeta de datos (ver arriba)
3. Reemplazar `licencias.db` con tu backup
4. Abrir nuevamente la aplicación

## 📊 Uso del sistema

### 1. Nueva licencia
- Ir a la pestaña **"➕ Nueva licencia"**
- Completar todos los campos obligatorios (*)
- Hacer clic en **"💾 Guardar licencia"**

### 2. Buscar y gestionar
- Ir a la pestaña **"🔎 Listado / Gestión"**
- Aplicar filtros según necesites
- Ver estadísticas en tiempo real
- Exportar a CSV o Excel
- Marcar como cargada en GEI (con fecha personalizable)

### 3. Editar o eliminar
- Ir a la pestaña **"✏️ Editar / Eliminar"**
- Ingresar el ID de la licencia
- Hacer clic en **"📋 Cargar datos"**
- Modificar los campos necesarios
- Guardar cambios o eliminar

### 4. Reporte mensual
- Ir a la pestaña **"📅 Reporte mensual"**
- Seleccionar el mes
- Ver estadísticas y alertas
- Presionar **Ctrl+P** para imprimir
- O descargar en CSV/Excel

## 🖨️ Imprimir reportes

1. Ir a **"📅 Reporte mensual"**
2. Seleccionar el mes deseado
3. Presionar **Ctrl+P** (Windows) o **Cmd+P** (Mac)
4. Configurar:
   - Orientación: **Horizontal**
   - Márgenes: **Mínimos**
   - Destino: Impresora o "Guardar como PDF"
5. Imprimir

## 🛠️ Requisitos del sistema

### Para ejecutar directamente (desarrollo):
- Python 3.8 o superior
- Windows 10/11, Linux o macOS
- 100 MB de espacio en disco
- pip para instalar dependencias

### Para versión portable (distribución):
- Windows 10/11 (64 bits)
- 2 GB RAM mínimo
- 200 MB espacio en disco
- Navegador web moderno
- **NO requiere instalar Python** (viene incluido)

## 📦 Dependencias

```
streamlit>=1.31.0
pandas>=2.2.3
sqlmodel>=0.0.25
openpyxl>=3.1.2
python-dateutil>=2.9.0
pyinstaller>=6.16.0  # Opcional (método alternativo menos recomendado)
```

**Nota:** Se recomienda usar la versión portable en lugar de PyInstaller. Ver [README_DISTRIBUCION.md](README_DISTRIBUCION.md) para más detalles.

## 🐛 Solución de problemas

### Windows Defender bloquea la aplicación
1. Clic en "Más información"
2. Clic en "Ejecutar de todas formas"
3. Es seguro, no es malware

### No se puede guardar datos
- Verificar permisos en la carpeta AppData
- En algunos casos: ejecutar `INICIAR.bat` como Administrador

### La aplicación no se abre en el navegador
- Abrir manualmente: `http://localhost:8501`
- Verificar que no haya otra instancia corriendo
- Probar con otro navegador (Chrome, Edge, Firefox)

### Error "Puerto 8501 en uso"
```bash
# Cerrar otras instancias o cambiar puerto
streamlit run app.py --server.port 8502
```

### Problemas con Python embebido
- Ver la guía detallada: [README_DISTRIBUCION.md](README_DISTRIBUCION.md)
- Verificar que `python311._pth` esté correctamente configurado
- Asegurar que pip esté instalado en el Python portable

## 🔄 Actualizar la aplicación

```bash
# Descargar últimos cambios
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Los datos NO se pierden (están en AppData)
```

## 📁 Estructura del proyecto

```
licencias_mza/
├── app.py                        # Aplicación principal
├── requirements.txt              # Dependencias
├── run.bat                       # Ejecutar en Windows (desarrollo)
├── run.sh                        # Ejecutar en Linux/Mac (desarrollo)
├── INICIAR.bat                   # Launcher para versión portable
├── README.md                     # Documentación principal
├── README_DISTRIBUCION.md        # Guía para generar versión portable
├── INSTRUCCIONES_USUARIO.txt     # Instrucciones para usuarios finales
├── LICENSE                       # Licencia MIT
├── .gitignore                    # Archivos ignorados por Git
└── .venv/                        # Entorno virtual (no se sube a Git)
```

### Archivos deprecados (no usar)
```
├── licencias.spec        # ❌ PyInstaller (genera errores importlib_metadata)
└── build_exe.bat         # ❌ Método antiguo con PyInstaller
```

**Nota:** Para distribución, usar el método de Python portable descrito en [README_DISTRIBUCION.md](README_DISTRIBUCION.md)
## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## � Documentación adicional

- **[README_DISTRIBUCION.md](README_DISTRIBUCION.md)** - Guía completa para generar versión portable
- **[INSTRUCCIONES_USUARIO.txt](INSTRUCCIONES_USUARIO.txt)** - Instrucciones para usuarios finales
- **[LICENSE](LICENSE)** - Licencia MIT del proyecto

## �📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Nicolas Maure**
- 🌐 Website: [nicomaure.com.ar](https://nicomaure.com.ar)
- 📧 Email: Contacto a través del sitio web

## 🙏 Agradecimientos

- Secretaría Escolar de Mendoza
- Comunidad de Streamlit
- Todos los contribuidores

## 📞 Soporte

Para problemas técnicos o sugerencias:
1. Abrir un [Issue en GitHub](https://github.com/nicomaure/licencias_mza/issues)
2. Contactar al desarrollador

---

<div align="center">

🗂️ **Sistema de Gestión de Licencias v2.0**

Desarrollado por [Nicolas Maure](https://nicomaure.com.ar)

Secretaría Escolar - Mendoza, Argentina

</div>


