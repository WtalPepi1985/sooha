<p align="center">
  <img src="assets/Logo.png" alt="SOOHA Logo" width="400"/>
</p>

# SOOHA – Screen Off Over Home Assistant

Windows Tray-App, die einen Monitor über Home Assistant ein- und ausschalten kann — und gleichzeitig Windows-Systemdaten als Sensoren an HA meldet.

---

## Wie es funktioniert

```
HA Dashboard / Automation
    ↓
HA MQTT Integration  →  MQTT Broker  →  SOOHA.exe (Windows Tray)
                                              ↓
                                     Windows API (WM_SYSCOMMAND)
                                              ↓
                                        Monitor Ein / Aus
```

Beim Start sendet SOOHA eine MQTT Discovery Message — HA erkennt alle Entities automatisch, ohne manuelle YAML-Konfiguration.

---

## Home Assistant Entities

| Entity | Typ | Beschreibung |
|---|---|---|
| `switch.sooha_screen` | Switch | Monitor ein-/ausschalten |
| `sensor.sooha_version` | Sensor | Laufende SOOHA-Version |
| `sensor.sooha_uptime` | Sensor | Windows Uptime (z.B. „2d 5h 30m") |
| `sensor.sooha_cpu` | Sensor | CPU-Auslastung in % (optional) |
| `sensor.sooha_ram` | Sensor | RAM-Auslastung in % (optional) |
| `sensor.sooha_win_updates` | Sensor | Ausstehende Windows-Updates (optional, alle 2h) |

Alle Entities zeigen **unavailable** wenn SOOHA nicht läuft.

---

## Voraussetzungen

- Windows 10 / 11 (oder Windows Server 2019+)
- MQTT Broker im Netz (z.B. Mosquitto Add-on in Home Assistant)
- Home Assistant mit MQTT Integration

---

## Installation

1. `SOOHA_vX.Y.Z.exe` herunterladen
2. In einen eigenen Ordner legen (z.B. `C:\Programme\SOOHA\`)
3. Starten — `config.json` wird automatisch daneben erstellt
4. Im Tray-Menü → **Einstellungen…** öffnen und MQTT-Daten eintragen
5. Im Tray-Menü → **Autostart aktivieren**

---

## Einstellungen

Über das Tray-Menü → **Einstellungen…**:

### Tab: MQTT

| Feld | Beschreibung |
|---|---|
| Host | IP/Hostname des MQTT Brokers |
| Port | Standard: `1883` |
| Benutzername / Passwort | Falls der Broker Auth erfordert |
| Gerätename | Anzeigename in Home Assistant |
| Geräte-ID | Technische ID (eindeutig, keine Leerzeichen) |

### Tab: Home Assistant

| Feld | Beschreibung |
|---|---|
| URL | z.B. `http://homeassistant.local:8123` |
| Token | Long-Lived Access Token aus HA |

### Tab: Features

**HA Sensoren (via MQTT → Home Assistant)**

| Feature | Entity | Intervall |
|---|---|---|
| Windows Uptime | `sensor.sooha_uptime` | 60s |
| CPU-Auslastung | `sensor.sooha_cpu` | 60s |
| RAM-Auslastung | `sensor.sooha_ram` | 60s |
| Windows Updates | `sensor.sooha_win_updates` | 2h |

**Tray-Menü**

| Feature | Beschreibung |
|---|---|
| Reboot-Option | „Windows neu starten…" mit Bestätigungsdialog |
| MQTT-Status | Verbindungsstatus im Tooltip (✓ / ✗) |

---

## Tray-Tooltip

```
SOOHA  |  Screen: EIN  ·  Uptime: 2d 5h 30m  ·  MQTT: ✓
```

---

## Tray-Menü

| Eintrag | Funktion |
|---|---|
| Screen: EIN / AUS | Aktueller Zustand (nicht klickbar) |
| Screen einschalten | Monitor an + HA State aktualisieren |
| Screen ausschalten | Monitor aus + HA State aktualisieren |
| Windows neu starten… | Reboot mit Bestätigungsdialog (optional) |
| Autostart aktivieren | Eintrag in Windows Registry setzen |
| Einstellungen… | Konfigurationsfenster öffnen |
| Beenden | App sauber beenden (meldet sich als offline in HA) |

---

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md).
