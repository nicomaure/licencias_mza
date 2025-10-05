# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Recolectar metadatos de streamlit y otros paquetes
datas = []
datas += collect_data_files('streamlit', include_py_files=True)
datas += collect_data_files('streamlit.runtime')
datas += collect_data_files('altair')
datas += collect_data_files('pandas')

# Recolectar todos los submódulos de streamlit
hiddenimports = []
hiddenimports += collect_submodules('streamlit')
hiddenimports += collect_submodules('streamlit.runtime')
hiddenimports += collect_submodules('streamlit.runtime.scriptrunner')
hiddenimports += [
    'streamlit.web.cli',
    'streamlit.runtime.legacy_caching',
    'streamlit.runtime.caching',
    'pandas',
    'sqlmodel',
    'sqlalchemy',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.sql.default_comparator',
    'openpyxl',
    'dateutil',
    'dateutil.relativedelta',
    'pydantic',
    'pydantic_core',
    'pydantic_core._pydantic_core',
    'altair',
    'jinja2',
    'pyarrow',
    'importlib_metadata',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements',
    'protobuf',
    'google.protobuf',
    'tornado',
    'tornado.web',
    'watchdog',
    'click',
    'requests',
    'PIL',
    'PIL._imaging',
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'numpy.testing'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LicenciasEscolares',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LicenciasEscolares',
)