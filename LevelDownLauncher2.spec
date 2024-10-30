# LevelDownLauncher2.spec

from PyInstaller.utils.hooks import collect_data_files

# Paths to your data files: images and config files
data_files = [
    ('assets/config/config.json', 'assets/config'),
    ('assets/config/version.json', 'assets/config'),
    ('assets/config/xiLoader.exe', 'assets/config'),
    ('assets/images/ashita.png', 'assets/images'),
    ('assets/images/ashitatxt.png', 'assets/images'),
    ('assets/images/launcher.png', 'assets/images'),
    ('assets/images/ld.ico', 'assets/images'),             # Icon file
    ('assets/images/level down loading.png', 'assets/images'),
    ('assets/images/level down.png', 'assets/images'),
    ('assets/images/loadingbar 0.png', 'assets/images'),
    ('assets/images/loadingbar 10 copy.png', 'assets/images'),
    ('assets/images/loadingbar 25 copy.png', 'assets/images'),
    ('assets/images/loadingbar 50 copy.png', 'assets/images'),
    ('assets/images/loadingbar 75 copy.png', 'assets/images'),
    ('assets/images/loadingbar 1000 copy.png', 'assets/images'),
    ('assets/images/stand copy.png', 'assets/images'),
    ('assets/images/wallpaper.png', 'assets/images'),
    ('assets/images/wallpaper2 copy.png', 'assets/images'),
    ('assets/images/wiki.png', 'assets/images'),
    ('assets/images/wikitxt.png', 'assets/images'),
    ('assets/images/windower.png', 'assets/images'),
    ('assets/images/windowertxt.png', 'assets/images'),
]

a = Analysis(
    ['main.py'],               # Main entry script
    pathex=['./'],             # Root path for the project
    binaries=[],               # No extra binary files
    datas=data_files,          # Include all specified data files
    hiddenimports=[
        "PyQt5.QtWebEngineWidgets", "feedparser", "bs4"
    ],                         # Hidden imports PyInstaller might miss
    hookspath=[],              # Custom hook scripts if needed
    runtime_hooks=[],          # Runtime hooks if necessary
    excludes=[],               # Modules to exclude
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
    debug=False,                         # Set to True for debugging
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                            # Use UPX compression if desired
    console=False,                       # Set to True if console output is needed
    icon='assets/images/ld.ico'          # Path to the icon file
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
