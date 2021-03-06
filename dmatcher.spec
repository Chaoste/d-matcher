# -*- mode: python -*-

import os
import sys

DEBUG = (os.getenv('DEBUG') or '').lower() == 'true'

block_cipher = None

app_name = 'DMatcher-DEBUG' if DEBUG else 'DMatcher'

dir = os.getcwd()

# https://pythonhosted.org/PyInstaller/spec-files.html#adding-data-files
added_files = [
  ( os.path.join(dir, 'dmatcher.kv'), '.' ),
  ( os.path.join(dir, 'res', 'background.jpg'), os.path.join('.', 'res') ),
  ( os.path.join(dir, 'res', 'favicon-v2.ico'), os.path.join('.', 'res') ),
]

a = Analysis(['client.py'],
             pathex=['/Users/thomas/work/repos/d-matcher'],
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
               name=app_name)

app = BUNDLE(coll,
             name=f'{app_name}.app',
             icon=os.path.join(dir, 'res', 'favicon-v2.icns'),
             bundle_identifier=None)

os.system("pushd dist")
os.system(f"hdiutil create ./dist/{app_name}.dmg -srcfolder ./dist/{app_name}.app -ov")
os.system("popd")
