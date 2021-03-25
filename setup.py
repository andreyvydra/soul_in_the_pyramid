import PyInstaller.__main__


PyInstaller.__main__.run([
    'main.py',
    'camera.py',
    'sprites.py',
    'settings.py',
    '-F',
    '--noconsole',
    '--add-data=data;.\\data',
])
