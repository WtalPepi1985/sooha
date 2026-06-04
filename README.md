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

## Konfiguration

`config.json` im Programmverzeichnis:

```json
{
  "mqtt_host": "10.10.4.211",
  "mqtt_port": 1883,
  "mqtt_username": "",
  "mqtt_password": "",
  "device_id": "sooha_screen",
  "device_name": "SOOHA Screen"
}
```

---

## Home Assistant

Nach dem ersten Start der App erscheint automatisch:

- **Entity:** `switch.sooha_screen`
- **Name:** SOOHA Screen

Keine YAML-Konfiguration nötig.

---

## Tray-Menü

| Eintrag | Funktion |
|---|---|
| Screen: EIN / AUS | Aktueller Zustand (nicht klickbar) |
| Screen einschalten | Monitor an + HA State aktualisieren |
| Screen ausschalten | Monitor aus + HA State aktualisieren |
| Autostart aktivieren | Eintrag in Windows Registry setzen |
| Beenden | App beenden |

---

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md).
