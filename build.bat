@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"

SET _DEACTIVE_VENV=0

IF [%_OLD_VIRTUAL_PROMPT%] == [] (
    CALL venv\Scripts\activate.bat
    SET _DEACTIVE_VENV=1
)

if exist build\ (
  rd /s /q "build\"
)

if exist dist\ (
  rd /s /q "dist\"
)

pyinstaller --noconsole --onefile --uac-admin php-webview.py

xcopy /E www\ dist\www\
xcopy /E bin\ dist\bin\

if exist build\ (
  rd /s /q "build\"
)

echo.
echo OK: Build generated in 'dist' folder.
echo.

IF [%_DEACTIVE_VENV%] equ 1 (
    SET _DEACTIVE_VENV=
    venv\Scripts\deactivate.bat
)