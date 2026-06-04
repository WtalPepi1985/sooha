# Changelog

All notable changes to SOOHA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Icon-Datei (`sooha.ico`) für PyInstaller Build
- MQTT-Authentifizierung testen (EMQX Username/Passwort)
- Konfiguration über Tray-Menü editierbar
- Mehrere Monitore unterstützen

---

## [0.1.0] - 2026-06-04

### Added
- Tray-App (`main.py`) mit Monitor-Icon (grün = ein, grau = aus)
- Tray-Menü: Screen ein/ausschalten, Autostart-Toggle, Beenden
- MQTT-Client (`mqtt_client.py`) mit Auto-Reconnect und Backoff
- Home Assistant MQTT Discovery → `switch.sooha_screen` erscheint automatisch
- Monitor-Steuerung via Windows API (`screen.py`, `ctypes` + `WM_SYSCOMMAND`)
- Zustandsverfolgung intern (kein DDC/CI erforderlich)
- `config.json` für MQTT-Host, Port, Credentials und Gerätenamen
- `build.bat` für PyInstaller One-File Build → `dist\SOOHA.exe`
- `install.bat` für manuellen Autostart-Eintrag in der Registry

[Unreleased]: https://github.com/WtalPepi1985/sooha/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/WtalPepi1985/sooha/releases/tag/v0.1.0
