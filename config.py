import json
from pathlib import Path

FILE = Path(__file__).parent / "config.json"

DEFAULTS = {
    "mqtt_host": "10.10.4.211",
    "mqtt_port": 1883,
    "mqtt_username": "",
    "mqtt_password": "",
    "device_id": "sooha_screen",
    "device_name": "SOOHA Screen",
    "ha_url": "http://10.10.4.21:8123",
    "ha_token": "",
    "feature_update_notify": True,
    "feature_runtime": True,
    "feature_reboot": False,
    "feature_mqtt_status": True,
}


def load() -> dict:
    try:
        with open(FILE, encoding="utf-8") as f:
            return {**DEFAULTS, **json.load(f)}
    except FileNotFoundError:
        return DEFAULTS.copy()


def save(data: dict):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
