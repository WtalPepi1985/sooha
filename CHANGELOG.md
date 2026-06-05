# Changelog

All notable changes to SOOHA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Mehrere Monitore unterstützen

---

## [1.0.0] - 2026-06-05

Erster stabiler Release. SOOHA ist ab sofort als fertige Windows-Tray-App für Smarthome-Displays einsetzbar — PCs und Mini-PCs, auf denen Windows als Visualisierungsrechner läuft (z.B. Kiosk-Displays mit HA-Dashboard).

### Added
- **Single-Instance-Schutz** — zweiter Start zeigt MessageBox und beendet sich sofort (Windows Mutex)
- **Restart-Dialog nach Einstellungen** — statt einfachem Hinweis: Buttons „Neu starten", „Beenden", „Weiter laufen"
- **README** um Einsatzzweck für Smarthome-Displays erweitert (Wanddisplay, Kiosk-PC, Büromonitor)

### Stable feature set
- Monitor ein-/ausschalten via HA Switch (`switch.<device_id>`)
- MQTT Discovery — alle Entities erscheinen automatisch in HA, kein YAML nötig
- HA Sensoren: Uptime, CPU, RAM (optional)
- Toast-Benachrichtigungen und Quittierungsdialog aus HA heraus
- Text-Entity in HA zum direkten Versenden von Nachrichten
- Multi-Device-fähig über individuelle Geräte-ID
- Autostart via Windows Registry
- Dunkles Einstellungsfenster mit MQTT-Verbindungstest

---

## [0.4.4] - 2026-06-05

### Added
- **Single-Instance-Schutz** via Windows Mutex — doppelter Start wird verhindert, MessageBox weist auf den laufenden System-Tray-Eintrag hin
- **Restart-Dialog nach Einstellungen speichern** — drei Optionen: „Neu starten" (startet neue Instanz), „Beenden", „Weiter laufen"
- Mutex wird vor Neustart freigegeben damit die neue Instanz starten kann

---

## [0.4.3] - 2026-06-05

### Added
- **Quittierungspflicht** (`feature_notify_confirm` in Settings) — statt Toast erscheint ein
  always-on-top Dialog mit rotem Header, der offen bleibt bis "Quittieren" geklickt wird.
  Nach Quittierung: publish auf `sooha/<device_id>/notify/ack` (Payload: `quittiert`) und
  Text-Entity wird geleert. HA-Automationen können auf das Ack-Topic triggern.

---

## [0.4.2] - 2026-06-05

### Added
- **HA Text-Entity** `text.<device_id>_notify` — erscheint automatisch in HA via MQTT Discovery.
  Text eingeben → Enter → Toast-Notification auf dem PC. Zeigt zuletzt gesendete Meldung an.
  Automationen können weiterhin direkt per `mqtt.publish` auf `sooha/<device_id>/notify` publishen.

---

## [0.4.1] - 2026-06-05

### Added
- **Toast-Benachrichtigungen** — MQTT-Topic `sooha/<device_id>/notify` zeigt eine Windows-Benachrichtigung an
  - Plain text: `Pumpe ausgefallen!` → Titel "SOOHA", Text der Payload
  - JSON: `{"title": "Störmeldung", "message": "Pumpe ausgefallen!"}` → eigener Titel möglich
  - HA-Nutzung: `mqtt.publish` in einer Automation (kein Discovery nötig)

---

## [0.4.0] - 2026-06-05

### Fixed
- **Screen einschalten** — `turn_on()` sendet jetzt zuerst ein `mouse_event(MOUSEEVENTF_MOVE)` bevor `SC_MONITORPOWER=-1` geschickt wird. Nur `SendMessage` reicht nicht bei Monitoren die in Hardware-Sleep sind.
- **Multi-Gerät MQTT** — Alle MQTT-Topics und die Client-ID werden jetzt aus der `device_id` generiert (`sooha/<device_id>/...`). Zwei SOOHA-Instanzen auf verschiedenen PCs brauchen jetzt nur unterschiedliche `device_id` (z.B. `sooha_flur`, `sooha_buero`) — keine gegenseitigen Konflikte mehr.

### Removed
- **HA Token + Update-Features** komplett entfernt — `ha_client.py`, HA-Tab in Einstellungen, `ha_url`/`ha_token` aus Config, `feature_sensor_win_updates` und `WIN_UPDATE_INTERVAL` aus Code
- Einstellungen haben jetzt nur noch zwei Tabs: MQTT und Features

### Changed
- MQTT `client_id` ist jetzt `sooha_<device_id>` statt fix `"sooha"`
- Sensor-Discovery-Topics und `unique_id`s enthalten jetzt die `device_id` (z.B. `sensor.sooha_flur_uptime`)
- `clean_session=True` im MQTT-Client

---

## [0.3.4] - 2026-06-04

### Added
- `sensor.sooha_version` — meldet die laufende SOOHA-Version an HA (immer aktiv, alle 60s)
- `sensor.sooha_win_updates` — Anzahl ausstehender Windows-Updates via PowerShell COM-Objekt, alle 2 Stunden (optional)
- **MQTT Availability** — alle HA-Entities zeigen automatisch „unavailable" wenn SOOHA nicht läuft (Last Will Testament + sauberes Offline beim Beenden/Reboot)

### Removed
- HA-Update-Check entfernt (`feature_update_notify`) — ersetzt durch Windows-Update-Sensor

### Changed
- Beenden im Tray-Menü sendet jetzt sauber „offline" vor dem Exit

---

## [0.3.3] - 2026-06-04

### Fixed
- `config.json` wurde neben der `.exe` erstellt statt im PyInstaller-Temp-Verzeichnis (`sys.executable` statt `__file__`)

---

## [0.3.2] - 2026-06-04

### Added
- `config.json` wird beim ersten Start automatisch mit Standardwerten angelegt

---

## [0.3.1] - 2026-06-04

### Fixed
- `sensors.py` fehlte in der SOURCES-Liste von `build-windows.sh` → ImportError beim Start

---

## [0.3.0] - 2026-06-04

### Added
- **MQTT-Sensoren** via HA Discovery (kein YAML nötig):
  - `sensor.sooha_uptime` — Windows Uptime (z.B. „2d 5h 30m"), alle 60s
  - `sensor.sooha_cpu` — CPU-Auslastung in % via psutil (optional)
  - `sensor.sooha_ram` — RAM-Auslastung in % via psutil (optional)
- `sensors.py` — Windows Uptime via `GetTickCount64`, CPU/RAM via `psutil`
- Einstellungen → Features in zwei Bereiche aufgeteilt: „HA Sensoren" und „Tray-Menü"

### Fixed
- Screen ging nicht aus: `HWND_BROADCAST` war `-1` (= `HWND_TOPMOST`) statt `0xFFFF`
- Explizite `ctypes`-Argtypes verhindert stille Typkonvertierungsfehler
- Screen-Off doppelt abgesichert: `SendMessage` (Desktop) + `PostMessage` (Broadcast)
- State-Sync: `check_woken()` via `GetLastInputInfo` erkennt wenn Maus/Tastatur den Screen weckt

### Changed
- `requirements.txt` um `psutil` ergänzt

---

## [0.2.0] - 2026-06-04

### Added
- Einstellungs-Fenster (`settings.py`) — Dark-Theme, 3 Tabs: MQTT, Home Assistant, Features
- Tab **MQTT**: Host, Port, Benutzername, Passwort, Gerätename, Geräte-ID + Verbindungstest
- Tab **Home Assistant**: URL, Token + Verbindungstest mit HA-Versionsanzeige
- Tab **Features**: 4 ein-/ausschaltbare Optionen (Checkboxen)
- HA-Client (`ha_client.py`) mit Update-Check alle 5 Minuten
- `config.py` als gemeinsames Config-Modul mit Defaults und Fallback

### Changed
- `config.json` um HA-URL, HA-Token und alle Feature-Flags erweitert
- `requirements.txt` um `requests` ergänzt

---

## [0.1.0] - 2026-06-04

### Added
- Tray-App (`main.py`) mit Monitor-Icon (grün = ein, grau = aus)
- Tray-Menü: Screen ein/ausschalten, Autostart-Toggle, Beenden
- MQTT-Client (`mqtt_client.py`) mit Auto-Reconnect und Backoff
- Home Assistant MQTT Discovery → `switch.sooha_screen` erscheint automatisch
- Monitor-Steuerung via Windows API (`screen.py`, `ctypes` + `WM_SYSCOMMAND`)
- `config.json` für MQTT-Host, Port, Credentials und Gerätenamen
- `build.bat` für PyInstaller One-File Build → `dist\SOOHA.exe`
- `install.bat` für manuellen Autostart-Eintrag in der Registry

[Unreleased]: https://github.com/WtalPepi1985/sooha/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/WtalPepi1985/sooha/compare/v0.4.4...v1.0.0
[0.4.4]: https://github.com/WtalPepi1985/sooha/compare/v0.4.3...v0.4.4
[0.4.3]: https://github.com/WtalPepi1985/sooha/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/WtalPepi1985/sooha/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/WtalPepi1985/sooha/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/WtalPepi1985/sooha/compare/v0.3.4...v0.4.0
[0.3.4]: https://github.com/WtalPepi1985/sooha/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/WtalPepi1985/sooha/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/WtalPepi1985/sooha/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/WtalPepi1985/sooha/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/WtalPepi1985/sooha/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/WtalPepi1985/sooha/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/WtalPepi1985/sooha/releases/tag/v0.1.0
