# -*- mode: python -*-

block_cipher = None


a = Analysis(['client.py'],
             pathex=['/Users/thomas/work/repos/d-matcher'],
             binaries=[],
             datas=[],
             hiddenimports=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='client',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='res/favicon-v2.ico')
app = BUNDLE(exe,
             name='client.app',
             icon='res/favicon-v2.ico',
             bundle_identifier=None)
