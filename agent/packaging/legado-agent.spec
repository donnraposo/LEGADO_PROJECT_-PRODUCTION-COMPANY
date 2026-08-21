# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path


agent_dir = Path(SPECPATH).parent
source_dir = agent_dir / "src"

analysis = Analysis(
    [str(source_dir / "legado_agent" / "main.py")],
    pathex=[str(source_dir)],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "ruff"],
    noarchive=False,
    optimize=1,
)

openssl_names = {"libcrypto-3-x64.dll", "libssl-3-x64.dll"}
analysis.binaries = [
    item for item in analysis.binaries if Path(item[0]).name.lower() not in openssl_names
]
python_dll_dir = Path(sys.base_prefix) / "DLLs"
for openssl_name in sorted(openssl_names):
    openssl_dll = python_dll_dir / openssl_name
    if not openssl_dll.is_file():
        raise FileNotFoundError(f"DLL SSL do runtime Python não encontrada: {openssl_dll}")
    analysis.binaries.append((openssl_name, str(openssl_dll), "BINARY"))

python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="LegadoAgent",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)

bundle = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="LegadoAgent",
)
