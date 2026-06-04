import json
import time
import threading
import paho.mqtt.client as mqtt

DISCOVERY_TOPIC = "homeassistant/switch/sooha_screen/config"
STATE_TOPIC = "sooha/screen/state"
COMMAND_TOPIC = "sooha/screen/set"


class MqttClient:
    def __init__(self, config: dict, on_turn_on, on_turn_off):
        self._config = config
        self._on_turn_on = on_turn_on
        self._on_turn_off = on_turn_off
        self._client = mqtt.Client(client_id="sooha", clean_session=False)
        self._connected = False

        if config.get("mqtt_username"):
            self._client.username_pw_set(config["mqtt_username"], config.get("mqtt_password", ""))

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        self._client.will_set(STATE_TOPIC, "OFF", retain=True)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            self._publish_discovery()
            client.subscribe(COMMAND_TOPIC)

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode().strip().upper()
        if payload == "ON":
            self._on_turn_on()
        elif payload == "OFF":
            self._on_turn_off()

    def _publish_discovery(self):
        device_id = self._config.get("device_id", "sooha_screen")
        device_name = self._config.get("device_name", "SOOHA Screen")
        payload = {
            "name": device_name,
            "unique_id": device_id,
            "state_topic": STATE_TOPIC,
            "command_topic": COMMAND_TOPIC,
            "payload_on": "ON",
            "payload_off": "OFF",
            "retain": True,
            "device": {
                "identifiers": [device_id],
                "name": device_name,
                "model": "SOOHA",
                "manufacturer": "WtalPepi1985",
            },
        }
        self._client.publish(DISCOVERY_TOPIC, json.dumps(payload), retain=True)

    def publish_state(self, on: bool):
        self._client.publish(STATE_TOPIC, "ON" if on else "OFF", retain=True)

    def start(self):
        host = self._config.get("mqtt_host", "10.10.4.211")
        port = self._config.get("mqtt_port", 1883)

        def _connect_loop():
            while True:
                try:
                    self._client.connect(host, port, keepalive=60)
                    self._client.loop_forever()
                except Exception:
                    time.sleep(10)

        t = threading.Thread(target=_connect_loop, daemon=True)
        t.start()

    def is_connected(self) -> bool:
        return self._connected
