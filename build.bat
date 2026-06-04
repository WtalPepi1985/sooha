@echo off
pyinstaller --onefile --windowed --name SOOHA main.py
echo.
echo Build fertig: dist\SOOHA.exe
pause
