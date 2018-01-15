# -*- mode: python -*-

block_cipher = None


a = Analysis(['Rotating_Coil_v3.py'],
             pathex=['F:\\Arq-James\\5 - Projetos\\1 - Desenvolvimento de Software\\Rotating Coil v3'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Rotating_Coil_v3',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
