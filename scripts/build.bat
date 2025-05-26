@echo off

python -m PyInstaller --onefile --windowed --name "AI-Launcher" ^
    --icon "assets/icon.ico" ^
    --hidden-import "pynput.keyboard" ^
    --hidden-import "pynput.keyboard._win32" ^
    --hidden-import "pynput._util.win32" ^
    --collect-all pynput ^
    src/main.py