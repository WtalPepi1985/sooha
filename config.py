import json
import sys
from pathlib import Path

# In a PyInstaller .exe, __file__ points to a temp dir — use sys.executable instead
if getattr(sys, "frozen", False):
    FILE = Path(sys.executable).parent / "config.json"
else:
    FILE = Path(__file__).parent / "config.json"

DEFAULTS = {
    "mqtt_host":     "10.10.4.211",
    "mqtt_port":     1883,
    "mqtt_username": "",
    "mqtt_password": "",
    "device_id":     "sooha_screen",
    "device_name":   "SOOHA Screen",
    # Tray-only features
    "feature_reboot":      False,
    "feature_mqtt_status": True,
    # MQTT sensor features (published to HA)
    "feature_runtime":    True,   # Windows Uptime sensor
    "feature_sensor_cpu": False,  # CPU % sensor
    "feature_sensor_ram": False,  # RAM % sensor
}


def load() -> dict:
    try:
        with open(FILE, encoding="utf-8") as f:
            return {**DEFAULTS, **json.load(f)}
    except FileNotFoundError:
        data = DEFAULTS.copy()
        save(data)
        return data


def save(data: dict):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
