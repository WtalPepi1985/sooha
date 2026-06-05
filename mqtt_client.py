import json
import time
import threading
import paho.mqtt.client as mqtt

SENSOR_DEFS = {
    "version": {
        "always": True,
        "ha": {
            "name": "SOOHA Version",
            "icon": "mdi:information-outline",
        },
    },
    "uptime": {
        "ha": {
            "name": "Windows Uptime",
            "icon": "mdi:timer-outline",
        },
    },
    "cpu": {
        "ha": {
            "name":                "CPU",
            "unit_of_measurement": "%",
            "state_class":         "measurement",
            "icon":                "mdi:cpu-64-bit",
        },
    },
    "ram": {
        "ha": {
            "name":                "RAM",
            "unit_of_measurement": "%",
            "state_class":         "measurement",
            "icon":                "mdi:memory",
        },
    },
}

FEATURE_MAP = {
    "uptime": "feature_runtime",
    "cpu":    "feature_sensor_cpu",
    "ram":    "feature_sensor_ram",
}


class MqttClient:
    def __init__(self, config: dict, on_turn_on, on_turn_off, on_notify=None):
        self._config      = config
        self._on_turn_on  = on_turn_on
        self._on_turn_off = on_turn_off
        self._on_notify   = on_notify
        self._connected   = False

        dev_id = config.get("device_id", "sooha_screen")
        self._init_topics(dev_id)

        # Unique client_id per device — prevents two SOOHA instances from kicking each other off the broker
        self._client = mqtt.Client(client_id=f"sooha_{dev_id}", clean_session=True)

        if config.get("mqtt_username"):
            self._client.username_pw_set(config["mqtt_username"], config.get("mqtt_password", ""))

        self._client.on_connect    = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message    = self._on_message
        self._client.will_set(self._avail_topic, "offline", retain=True)

    def _init_topics(self, dev_id: str):
        self._dev_id             = dev_id
        self._switch_disc        = f"homeassistant/switch/{dev_id}/config"
        self._state_topic        = f"sooha/{dev_id}/screen/state"
        self._command_topic      = f"sooha/{dev_id}/screen/set"
        self._avail_topic        = f"sooha/{dev_id}/status"
        self._notify_topic       = f"sooha/{dev_id}/notify"
        self._notify_state_topic = f"sooha/{dev_id}/notify/state"
        self._notify_ack_topic   = f"sooha/{dev_id}/notify/ack"
        self._notify_text_disc   = f"homeassistant/text/{dev_id}_notify/config"
        self._sensor_state       = {k: f"sooha/{dev_id}/sensor/{k}/state" for k in SENSOR_DEFS}
        self._sensor_disc        = {k: f"homeassistant/sensor/{dev_id}_{k}/config" for k in SENSOR_DEFS}

    # ── MQTT callbacks ────────────────────────────────────────────────────────

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            client.publish(self._avail_topic, "online", retain=True)
            self._publish_switch_discovery()
            self._publish_sensor_discovery()
            self._publish_notify_text_discovery()
            client.subscribe(self._command_topic)
            client.subscribe(self._notify_topic)

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False

    def _on_message(self, client, userdata, msg):
        if msg.topic == self._notify_topic:
            self._handle_notify(msg.payload.decode().strip())
            return
        payload = msg.payload.decode().strip().upper()
        if payload == "ON":
            self._on_turn_on()
        elif payload == "OFF":
            self._on_turn_off()

    def _handle_notify(self, raw: str):
        if not self._on_notify:
            return
        try:
            data = json.loads(raw)
            title   = data.get("title",   "SOOHA")
            message = data.get("message", "")
        except (json.JSONDecodeError, AttributeError):
            title   = "SOOHA"
            message = raw
        if message:
            self._client.publish(self._notify_state_topic, message, retain=True)
            self._on_notify(title, message)

    # ── Discovery ─────────────────────────────────────────────────────────────

    def _device_block(self) -> dict:
        dev_name = self._config.get("device_name", "SOOHA Screen")
        return {"identifiers": [self._dev_id], "name": dev_name, "model": "SOOHA", "manufacturer": "WtalPepi1985"}

    def _avail_block(self) -> dict:
        return {"topic": self._avail_topic, "payload_available": "online", "payload_not_available": "offline"}

    def _publish_switch_discovery(self):
        dev_name = self._config.get("device_name", "SOOHA Screen")
        payload = {
            "name":          dev_name,
            "unique_id":     self._dev_id,
            "state_topic":   self._state_topic,
            "command_topic": self._command_topic,
            "payload_on":    "ON",
            "payload_off":   "OFF",
            "retain":        True,
            "availability":  [self._avail_block()],
            "device":        self._device_block(),
        }
        self._client.publish(self._switch_disc, json.dumps(payload), retain=True)

    def _publish_sensor_discovery(self):
        for key in self._enabled_sensors():
            defn = SENSOR_DEFS[key]
            payload = {
                **defn["ha"],
                "unique_id":   f"{self._dev_id}_{key}",
                "state_topic": self._sensor_state[key],
                "availability": [self._avail_block()],
                "device":       self._device_block(),
            }
            self._client.publish(self._sensor_disc[key], json.dumps(payload), retain=True)

    def _publish_notify_text_discovery(self):
        payload = {
            "name":          "Benachrichtigung",
            "unique_id":     f"{self._dev_id}_notify",
            "command_topic": self._notify_topic,
            "state_topic":   self._notify_state_topic,
            "icon":          "mdi:bell-alert",
            "availability":  [self._avail_block()],
            "device":        self._device_block(),
        }
        self._client.publish(self._notify_text_disc, json.dumps(payload), retain=True)

    def _enabled_sensors(self) -> list:
        always   = [k for k, d in SENSOR_DEFS.items() if d.get("always")]
        optional = [k for k, flag in FEATURE_MAP.items() if self._config.get(flag)]
        return always + optional

    # ── Publish ───────────────────────────────────────────────────────────────

    def publish_state(self, on: bool):
        self._client.publish(self._state_topic, "ON" if on else "OFF", retain=True)

    def publish_sensors(self, values: dict):
        for key, value in values.items():
            if key in self._sensor_state:
                self._client.publish(self._sensor_state[key], str(value), retain=True)

    def publish_notify_ack(self):
        self._client.publish(self._notify_ack_topic, "quittiert", retain=False)
        self._client.publish(self._notify_state_topic, "", retain=True)

    def publish_offline(self):
        self._client.publish(self._avail_topic, "offline", retain=True)

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
