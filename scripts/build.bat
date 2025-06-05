@echo off

python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --add-data "src/assets;assets" ^
    --name "AI-Launcher" ^
    --icon "assets/icon.ico" ^
    --hidden-import "pynput.keyboard" ^
    --hidden-import "pynput.keyboard._win32" ^
    --hidden-import "pynput._util.win32" ^
    --exclude-module "matplotlib" ^
    --exclude-module "tkinter" ^
    --exclude-module "test" ^
    --exclude-module "unittest" ^
    --exclude-module "doctest" ^
    --exclude-module "pydoc" ^
    --exclude-module "pydantic.color" ^
    --exclude-module "pydantic.json" ^
    --exclude-module "pydantic.schema" ^
    --exclude-module "pydantic.mypy" ^
    --exclude-module "pydantic.networks" ^
    --exclude-module "email_validator" ^
    --exclude-module "sqlalchemy.dialects.mysql" ^
    --exclude-module "sqlalchemy.dialects.postgresql" ^
    --exclude-module "sqlalchemy.dialects.oracle" ^
    --exclude-module "sqlalchemy.dialects.mssql" ^
    --exclude-module "sqlalchemy.dialects.firebird" ^
    --exclude-module "sqlalchemy.dialects.sybase" ^
    --exclude-module "PIL" ^
    --exclude-module "pandas" ^
    --exclude-module "scipy" ^
    --exclude-module "IPython" ^
    --collect-all pynput ^
    --optimize 2 ^
    src/main.py
