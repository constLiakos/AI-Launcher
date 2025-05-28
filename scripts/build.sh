#!/bin/bash

pyinstaller \
    --onefile \
    --windowed \
    --add-data "src/assets:assets" \
    --name "AI-Launcher" \
    --hidden-import "pynput.keyboard" \
    --hidden-import "pynput.keyboard._xorg" \
    --hidden-import "pynput._util.xorg" \
    --hidden-import "Xlib.display" \
    --hidden-import "Xlib.X" \
    --collect-all pynput \
    src/main.py