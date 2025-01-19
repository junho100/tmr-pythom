# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# 현재 작업 디렉토리를 기준으로 src 경로 설정
src_path = os.path.abspath('src')

a = Analysis(
    ['run.py'],
    pathex=[
        src_path,  # src 디렉토리 경로 추가
        os.getcwd(),  # 현재 작업 디렉토리 추가
    ],
    binaries=[],
    datas=[
        ('gdx', 'gdx'),  # gdx 모듈 포함
        ('src', 'src'),  # src 디렉토리 전체를 포함
    ],
    hiddenimports=[
        'godirect',
        'bleak',
        'PyQt5',
        'pyqtgraph',
        'numpy',
        'requests',
        'ipaddress',
        'urllib.parse',
        'pathlib',
        'pkg_resources.py2_warn',
        'pkg_resources._vendor.packaging.version',
        'pkg_resources._vendor.packaging.specifiers',
        'pkg_resources._vendor.packaging.requirements',
        'pkg_resources._vendor.packaging.markers',
        'pkg_resources._vendor.pyparsing',
        'src.main',  # main 모듈 명시적 추가
        'src.login_window',  # 관련 모듈들도 추가
        'src.breathing_window',
        'src.api.user_api',
    ],
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
    name='breathing_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 디버깅을 위해 True로 유지
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
) 