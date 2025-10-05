
================================================================================
SISTEMA DE GESTIÓN DE LICENCIAS - SECRETARÍA ESCOLAR MENDOZA
INSTRUCCIONES DE INSTALACIÓN Y USO
================================================================================

┌────────────────────────────────────────────────────────────────────────────┐
│ OPCIÓN A: USO DIRECTO (RECOMENDADO PARA DESARROLLO)                       │
└────────────────────────────────────────────────────────────────────────────┘

1. Hacer doble clic en: run.bat

2. Esperar a que se instalen las dependencias (solo la primera vez)

3. La aplicación se abrirá automáticamente en el navegador

4. ¡Listo! Ya podés usar el sistema


┌────────────────────────────────────────────────────────────────────────────┐
│ OPCIÓN B: GENERAR EJECUTABLE (.EXE)                                       │
└────────────────────────────────────────────────────────────────────────────┘

PASO 1: GENERAR EL .EXE
-----------------------
1. Hacer doble clic en: build_exe.bat

2. Esperar a que termine el proceso (puede tardar varios minutos)

3. El ejecutable se creará en: dist\LicenciasEscolares\


PASO 2: PROBAR EL EJECUTABLE
-----------------------------
1. Ir a: dist\LicenciasEscolares\

2. Hacer doble clic en: LicenciasEscolares.exe

3. Se abrirá una ventana negra (no cerrarla)

4. El navegador se abrirá automáticamente con la aplicación


PASO 3: DISTRIBUIR A OTROS EQUIPOS
-----------------------------------
1. Comprimir TODA la carpeta: dist\LicenciasEscolares\
   (Clic derecho > Enviar a > Carpeta comprimida)

2. Compartir el archivo .zip

3. Los usuarios deben:
   - Descomprimir el archivo
   - Ejecutar LicenciasEscolares.exe
   - ¡Ya funciona!


┌────────────────────────────────────────────────────────────────────────────┐
│ UBICACIÓN DE LOS DATOS                                                     │
└────────────────────────────────────────────────────────────────────────────┘

Los datos se guardan en:
C:\Users\[TuUsuario]\AppData\Local\LicenciasEscolares\licencias.db

Ventajas:
✅ No hay problemas de permisos
✅ Los datos persisten aunque actualices la aplicación
✅ Fácil hacer backup (solo copiar el archivo .db)


┌────────────────────────────────────────────────────────────────────────────┐
│ CÓMO HACER BACKUP DE LOS DATOS                                            │
└────────────────────────────────────────────────────────────────────────────┘

1. Presionar: Windows + R

2. Escribir: %LOCALAPPDATA%\LicenciasEscolares

3. Copiar el archivo: licencias.db

4. Guardarlo en un lugar seguro (USB, nube, etc.)


┌────────────────────────────────────────────────────────────────────────────┐
│ CÓMO RESTAURAR UN BACKUP                                                   │
└────────────────────────────────────────────────────────────────────────────┘

1. Cerrar la aplicación si está abierta

2. Presionar: Windows + R

3. Escribir: %LOCALAPPDATA%\LicenciasEscolares

4. Reemplazar el archivo licencias.db con tu backup

5. Abrir nuevamente la aplicación


┌────────────────────────────────────────────────────────────────────────────┐
│ IMPRIMIR REPORTES                                                          │
└────────────────────────────────────────────────────────────────────────────┘

1. Ir a la pestaña: "📅 Reporte mensual"

2. Seleccionar el mes

3. Presionar: Ctrl + P

4. Opciones:
   - Seleccionar impresora para imprimir en papel
   - Seleccionar "Guardar como PDF" para guardar archivo
   
5. Ajustar orientación a "Horizontal" para mejor visualización


┌────────────────────────────────────────────────────────────────────────────┐
│ SOLUCIÓN DE PROBLEMAS COMUNES                                             │
└────────────────────────────────────────────────────────────────────────────┘

PROBLEMA: Windows Defender bloquea el .exe
SOLUCIÓN: 
  1. Clic en "Más información"
  2. Clic en "Ejecutar de todas formas"
  3. Es seguro, es tu propio ejecutable


PROBLEMA: No se puede guardar datos
SOLUCIÓN:
  1. Ejecutar como Administrador
  2. Verificar que la carpeta AppData no esté protegida


PROBLEMA: No se exporta a Excel
SOLUCIÓN:
  1. Cerrar todos los archivos Excel abiertos
  2. Intentar nuevamente


PROBLEMA: La aplicación no se abre en el navegador
SOLUCIÓN:
  1. Abrir manualmente el navegador
  2. Ir a: http://localhost:8501


┌────────────────────────────────────────────────────────────────────────────┐
│ REQUISITOS DEL SISTEMA                                                     │
└────────────────────────────────────────────────────────────────────────────┘

✅ Windows 10 (64 bits) o superior
✅ Windows 11 (64 bits)
✅ 2 GB RAM mínimo (4 GB recomendado)
✅ 500 MB espacio en disco
✅ Navegador web moderno (Chrome, Edge, Firefox)


┌────────────────────────────────────────────────────────────────────────────┐
│ CONTACTO Y SOPORTE                                                         │
└────────────────────────────────────────────────────────────────────────────┘

Para problemas técnicos o sugerencias, contactar al administrador del sistema.

================================================================================
Versión 2.0 - Sistema de Gestión de Licencias
Secretaría Escolar - Mendoza, Argentina
================================================================================