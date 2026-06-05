<p align="center">
  <img src="assets/Logo.png" alt="SOOHA Logo" width="400"/>
</p>

# SOOHA – Screen Off Over Home Assistant

Windows Tray-App, die einen Monitor über Home Assistant ein- und ausschalten kann, Windows-Systemdaten als Sensoren an HA meldet und Störmeldungen als Benachrichtigungen auf dem PC anzeigt.

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
| `switch.<device_id>` | Switch | Monitor ein-/ausschalten |
| `text.<device_id>_benachrichtigung` | Text | Nachricht eingeben → sofort als Notification anzeigen |
| `sensor.<device_id>_version` | Sensor | Laufende SOOHA-Version |
| `sensor.<device_id>_uptime` | Sensor | Windows Uptime (z.B. „2d 5h 30m") — optional |
| `sensor.<device_id>_cpu` | Sensor | CPU-Auslastung in % — optional |
| `sensor.<device_id>_ram` | Sensor | RAM-Auslastung in % — optional |

Alle Entities zeigen **unavailable** wenn SOOHA nicht läuft.

> `<device_id>` ist die in den Einstellungen konfigurierte Geräte-ID (Standard: `sooha_screen`).

---

## Benachrichtigungen / Störmeldungen

SOOHA kann Nachrichten von HA empfangen und auf dem PC anzeigen — als einfacher Toast oder als Quittierungsdialog.

**MQTT-Topic:** `sooha/<device_id>/notify`

**Payload — plain text:**
```
Pumpe Heizung ausgefallen!
```

**Payload — JSON mit eigenem Titel:**
```json
{"title": "Störmeldung", "message": "Pumpe Heizung ausgefallen!"}
```

**HA-Automation Beispiel:**
```yaml
service: mqtt.publish
data:
  topic: "sooha/sooha_screen/notify"
  payload: '{"title": "Störmeldung", "message": "Pumpe Heizung ausgefallen!"}'
```

Oder einfacher — Text direkt in HA in die `text.<device_id>_benachrichtigung` Entity eingeben.

### Quittierungspflicht

Mit aktivierter Option **Quittierungspflicht** in den Settings erscheint statt eines Toasts ein Dialog, der offen bleibt bis der User auf **Quittieren** klickt.

Nach der Quittierung published SOOHA auf `sooha/<device_id>/notify/ack` (Payload: `quittiert`) — HA-Automationen können darauf reagieren:

```yaml
trigger:
  platform: mqtt
  topic: "sooha/sooha_screen/notify/ack"
action:
  # z.B. Alarm stoppen, Logbuch-Eintrag
```

---

## Multi-Device

Mehrere SOOHA-Instanzen auf verschiedenen PCs sind möglich — jede braucht eine eigene **Geräte-ID** in den Einstellungen (z.B. `sooha_flur`, `sooha_buero`). Alle MQTT-Topics und HA-Entities werden automatisch danach benannt.

> **Hinweis:** Bei einer Änderung der Geräte-ID müssen die alten HA-Entities manuell gelöscht werden.

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
| Geräte-ID | Technische ID (eindeutig pro Gerät, keine Leerzeichen) |

### Tab: Features

**HA Sensoren (via MQTT → Home Assistant)**

| Feature | Entity | Intervall |
|---|---|---|
| Windows Uptime | `sensor.<id>_uptime` | 60s |
| CPU-Auslastung | `sensor.<id>_cpu` | 60s |
| RAM-Auslastung | `sensor.<id>_ram` | 60s |

**Benachrichtigungen**

| Feature | Beschreibung |
|---|---|
| Quittierungspflicht | Dialog statt Toast — bleibt offen bis Quittieren geklickt, sendet Ack an HA |

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
