# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置 - 完全独立版
HALO-FIT 外贸进销存系统
"""

block_cipher = None

a = Analysis(
    ['app_fixed.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'streamlit',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.runtime.runtime',
        'streamlit.runtime.caching',
        'streamlit.runtime.metrics',
        'streamlit.elements',
        'streamlit.delta_generator',
        'streamlit.uploaded_file_manager',
        'streamlit.web.server',
        'streamlit.web.server.stats',
        'streamlit.components',
        'streamlit.elements.arrow',
        'streamlit.elements.dataframe',
        'streamlit.elements.image',
        'pandas',
        'pandas._libs',
        'pandas._libs.tslibs',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.tslibs.npy',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'PIL._imaging',
    ],
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
    name='HALO-FIT-外贸进销存系统',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HALO-FIT-外贸进销存系统',
)
