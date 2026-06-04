import json
import time
import threading
import paho.mqtt.client as mqtt

SWITCH_DISCOVERY = "homeassistant/switch/sooha_screen/config"
STATE_TOPIC      = "sooha/screen/state"
COMMAND_TOPIC    = "sooha/screen/set"

# Sensor definitions: key → (discovery topic, state topic, HA config)
SENSOR_DEFS = {
    "uptime": {
        "discovery": "homeassistant/sensor/sooha_uptime/config",
        "state":     "sooha/sensor/uptime/state",
        "ha": {
            "name":       "Windows Uptime",
            "unique_id":  "sooha_uptime",
            "icon":       "mdi:timer-outline",
        },
    },
    "cpu": {
        "discovery": "homeassistant/sensor/sooha_cpu/config",
        "state":     "sooha/sensor/cpu/state",
        "ha": {
            "name":                  "CPU",
            "unique_id":             "sooha_cpu",
            "unit_of_measurement":   "%",
            "state_class":           "measurement",
            "icon":                  "mdi:cpu-64-bit",
        },
    },
    "ram": {
        "discovery": "homeassistant/sensor/sooha_ram/config",
        "state":     "sooha/sensor/ram/state",
        "ha": {
            "name":                  "RAM",
            "unique_id":             "sooha_ram",
            "unit_of_measurement":   "%",
            "state_class":           "measurement",
            "icon":                  "mdi:memory",
        },
    },
}


class MqttClient:
    def __init__(self, config: dict, on_turn_on, on_turn_off):
        self._config    = config
        self._on_turn_on  = on_turn_on
        self._on_turn_off = on_turn_off
        self._client    = mqtt.Client(client_id="sooha", clean_session=False)
        self._connected = False

        if config.get("mqtt_username"):
            self._client.username_pw_set(config["mqtt_username"], config.get("mqtt_password", ""))

        self._client.on_connect    = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message    = self._on_message
        self._client.will_set(STATE_TOPIC, "OFF", retain=True)

    # ── MQTT callbacks ────────────────────────────────────────────────────────

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            self._publish_switch_discovery()
            self._publish_sensor_discovery()
            client.subscribe(COMMAND_TOPIC)

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode().strip().upper()
        if payload == "ON":
            self._on_turn_on()
        elif payload == "OFF":
            self._on_turn_off()

    # ── Discovery ─────────────────────────────────────────────────────────────

    def _device_block(self) -> dict:
        dev_id   = self._config.get("device_id",   "sooha_screen")
        dev_name = self._config.get("device_name", "SOOHA Screen")
        return {"identifiers": [dev_id], "name": dev_name, "model": "SOOHA", "manufacturer": "WtalPepi1985"}

    def _publish_switch_discovery(self):
        dev_id   = self._config.get("device_id",   "sooha_screen")
        dev_name = self._config.get("device_name", "SOOHA Screen")
        payload = {
            "name":          dev_name,
            "unique_id":     dev_id,
            "state_topic":   STATE_TOPIC,
            "command_topic": COMMAND_TOPIC,
            "payload_on":    "ON",
            "payload_off":   "OFF",
            "retain":        True,
            "device":        self._device_block(),
        }
        self._client.publish(SWITCH_DISCOVERY, json.dumps(payload), retain=True)

    def _publish_sensor_discovery(self):
        enabled = self._enabled_sensors()
        for key in enabled:
            defn = SENSOR_DEFS[key]
            payload = {**defn["ha"], "state_topic": defn["state"], "device": self._device_block()}
            self._client.publish(defn["discovery"], json.dumps(payload), retain=True)

    def _enabled_sensors(self) -> list:
        mapping = {
            "uptime": "feature_runtime",
            "cpu":    "feature_sensor_cpu",
            "ram":    "feature_sensor_ram",
        }
        return [key for key, flag in mapping.items() if self._config.get(flag)]

    # ── Publish ───────────────────────────────────────────────────────────────

    def publish_state(self, on: bool):
        self._client.publish(STATE_TOPIC, "ON" if on else "OFF", retain=True)

    def publish_sensors(self, values: dict):
        """values: dict of sensor_key → value string, e.g. {"uptime": "2d 3h 15m"}"""
        for key, value in values.items():
            if key in SENSOR_DEFS:
                self._client.publish(SENSOR_DEFS[key]["state"], str(value), retain=True)

    def update_config(self, config: dict):
        self._config = config

    # ── Connection loop ───────────────────────────────────────────────────────

    def start(self):
        host = self._config.get("mqtt_host", "10.10.4.211")
        port = self._config.get("mqtt_port", 1883)

        def _loop():
            while True:
                try:
                    self._client.connect(host, port, keepalive=60)
                    self._client.loop_forever()
                except Exception:
                    time.sleep(10)

        threading.Thread(target=_loop, daemon=True).start()

    def is_connected(self) -> bool:
        return self._connected
