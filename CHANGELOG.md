# Changelog

All notable changes to SOOHA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Icon-Datei (`sooha.ico`) für PyInstaller Build
- Mehrere Monitore unterstützen

---

## [0.2.0] - 2026-06-04

### Added
- Einstellungs-Fenster (`settings.py`) — Dark-Theme, 3 Tabs: MQTT, Home Assistant, Features
- Tab **MQTT**: Host, Port, Benutzername, Passwort, Gerätename, Geräte-ID + Verbindungstest
- Tab **Home Assistant**: URL, Token + Verbindungstest mit HA-Versionsanzeige
- Tab **Features**: 4 ein-/ausschaltbare Optionen (Checkboxen)
- Feature **Update-Benachrichtigung**: HA-Updates werden im Tooltip und Menü angezeigt
- Feature **Laufzeit anzeigen**: App-Laufzeit im Tray-Tooltip (`2h 15m`)
- Feature **Reboot-Option**: „Windows neu starten…" im Tray-Menü mit Bestätigungsdialog
- Feature **MQTT-Status**: Verbindungsstatus im Tooltip (✓ / ✗)
- HA-Client (`ha_client.py`) mit Update-Check alle 5 Minuten
- `config.py` als gemeinsames Config-Modul mit Defaults und Fallback

### Changed
- `config.json` um HA-URL, HA-Token und alle Feature-Flags erweitert
- Tray-Tooltip zeigt jetzt zusammengesetzten Status-String
- `requirements.txt` um `requests` ergänzt

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
