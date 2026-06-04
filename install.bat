@echo off
REM Autostart in Registry eintragen (alternativ zum Tray-Menu)
set EXE=%~dp0dist\SOOHA.exe
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v SOOHA /t REG_SZ /d "\"%EXE%\"" /f
echo Autostart eingetragen: %EXE%
pause
