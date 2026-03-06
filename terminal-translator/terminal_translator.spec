# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Terminal Translator
Builds standalone executables for macOS, Windows, and Linux
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all textual data files (CSS, etc.)
textual_datas = collect_data_files('textual')

# Collect submodules
hidden_imports = collect_submodules('textual') + [
    'terminal_translator',
    'terminal_translator.knowledge_base',
    'terminal_translator.ai_translator',
    'terminal_translator.shell_manager',
]

a = Analysis(
    ['src/terminal_translator/main.py'],
    pathex=[],
    binaries=[],
    datas=textual_datas + [
        ('src/terminal_translator/knowledge_base.py', 'terminal_translator'),
        ('src/terminal_translator/styles.tcss', 'terminal_translator'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TerminalTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # TUI needs console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if sys.platform == 'win32' else 'assets/icon.icns' if sys.platform == 'darwin' else None,
)

# macOS app bundle (optional)
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='TerminalTranslator.app',
        icon='assets/icon.icns',
        bundle_identifier='dev.termtranslator.app',
        info_plist={
            'CFBundleName': 'Terminal Translator',
            'CFBundleDisplayName': 'Terminal Translator',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )
