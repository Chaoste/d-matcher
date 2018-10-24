# -*- mode: python -*-

import os

DEBUG = False

block_cipher = None

app_name = 'D-Matcher'

dir = os.getcwd()

# https://pythonhosted.org/PyInstaller/spec-files.html#adding-data-files
added_files = [
  ( os.path.join(dir, 'dmatcher.kv'), '.' ),
  ( os.path.join(dir, 'background.jpg'), '.' ),
]

a = Analysis(['client.py'],
             pathex=['/Users/thomas/work/repos/d-matcher/'],
             binaries=[],
             datas=added_files,
             hiddenimports=['src'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=app_name,
          debug=DEBUG,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=DEBUG )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='dmatcher')
