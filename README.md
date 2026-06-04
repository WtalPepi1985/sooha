# SOOHA – Screen Off Over Home Assistant

Windows Tray-App, die einen Monitor über Home Assistant ein- und ausschalten kann.

HA bekommt eine echte `switch`-Entity (`switch.sooha_screen`) via MQTT Discovery — steuerbar über Dashboard, Automationen oder Sprachassistent.

---

## Wie es funktioniert

```
HA Dashboard / Automation
    ↓
HA MQTT Integration  →  EMQX Broker  →  SOOHA.exe (Windows Tray)
                                              ↓
                                     Windows API (WM_SYSCOMMAND)
                                              ↓
                                        Monitor Ein / Aus
```

Beim Start sendet die App einmalig eine MQTT Discovery Message — HA erkennt das Gerät automatisch, ohne manuelle Konfiguration.

---

## Voraussetzungen

- Windows 10 / 11 (oder Windows Server 2019+)
- MQTT Broker im Netz (getestet mit EMQX)
- Home Assistant mit MQTT Integration

---

## Installation

**Aus dem Quellcode (Entwicklung):**

```bat
pip install -r requirements.txt
python main.py
```

**Als .exe bauen:**

```bat
build.bat
```

Die fertige `SOOHA.exe` liegt anschließend unter `dist\SOOHA.exe`.

**Autostart einrichten:**

Entweder über das Tray-Menü → *Autostart aktivieren*, oder einmalig `install.bat` ausführen.

---

## Einstellungen

Über das Tray-Menü → **Einstellungen…** öffnet sich ein Konfigurationsfenster mit drei Tabs:

### Tab: MQTT

| Feld | Beschreibung |
|---|---|
| Host | IP/Hostname des MQTT Brokers |
| Port | Standard: `1883` |
| Benutzername / Passwort | Optional, falls der Broker Auth erfordert |
| Gerätename | Anzeigename in Home Assistant |
| Geräte-ID | Technische ID (eindeutig, keine Leerzeichen) |

### Tab: Home Assistant

| Feld | Beschreibung |
|---|---|
| URL | z.B. `http://10.10.4.21:8123` |
| Token | Long-Lived Access Token aus HA |

### Tab: Features

| Feature | Beschreibung |
|---|---|
| Update-Benachrichtigung | Zeigt im Tooltip an, wenn HA-Updates verfügbar sind |
| Laufzeit anzeigen | App-Laufzeit im Tray-Tooltip (`2h 15m`) |
| Reboot-Option | „Windows neu starten…" im Tray-Menü (mit Bestätigung) |
| MQTT-Status anzeigen | Verbindungsstatus im Tooltip (✓ / ✗) |

Alle Verbindungen können direkt im Einstellungs-Fenster getestet werden.

---

## Tray-Tooltip

Der Tooltip zeigt je nach aktivierten Features einen kombinierten Status:

```
SOOHA  |  Screen: EIN  ·  Laufzeit: 2h 15m  ·  MQTT: ✓  ·  Updates: 2 verfügbar
```

---

## Tray-Menü

| Eintrag | Funktion |
|---|---|
| Screen: EIN / AUS | Aktueller Zustand (nicht klickbar) |
| ⚠ N Update(s) verfügbar | Hinweis wenn HA-Updates bereitstehen (optional) |
| Screen einschalten | Monitor an + HA State aktualisieren |
| Screen ausschalten | Monitor aus + HA State aktualisieren |
| Windows neu starten… | Reboot mit Bestätigungsdialog (optional) |
| Autostart aktivieren | Eintrag in Windows Registry setzen |
| Einstellungen… | Konfigurationsfenster öffnen |
| Beenden | App beenden |

---

## Home Assistant

Nach dem ersten Start der App erscheint automatisch:

- **Entity:** `switch.sooha_screen`
- **Name:** SOOHA Screen

Keine YAML-Konfiguration nötig.

---

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md).
