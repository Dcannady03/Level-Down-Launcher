# LevelDownLauncher2.spec
from PyInstaller.utils.hooks import collect_data_files

# Collect all files in assets and _internal
data_files = [
    ('assets', 'assets'),          # Places assets in root with exe
    ('_internal', '_internal'),    # Places _internal in root with exe
]

a = Analysis(
    ['main.py'],                   # Main entry script
    pathex=['./'],                 # Root path for the project
    binaries=[],                   # No extra binary files
    datas=data_files,              # Include all specified data files
    hiddenimports=[
        "PyQt5.QtWebEngineWidgets", "feedparser", "bs4"
    ],                             # Hidden imports PyInstaller might miss
    hookspath=[],                  # Custom hook scripts if needed
    runtime_hooks=[],              # Runtime hooks if necessary
    excludes=[],                   # Modules to exclude
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
)

# Compile with dependencies
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Configure the EXE, including the application icon
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LevelDownLauncher',
    debug=False,                   # Set to True for debugging
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                      # Use UPX compression if desired
    console=False,                 # Set to True if console output is needed
    icon='assets/images/ld.ico'    # Path to the icon file
)

# Collect the binaries, data, and zip files into the final distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='LevelDownLauncher'
)
