import json
import os
import sys
import threading
import winreg
from pathlib import Path

import pystray
from PIL import Image, ImageDraw

import screen as scr
from mqtt_client import MqttClient

CONFIG_FILE = Path(__file__).parent / "config.json"
AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "SOOHA"


def load_config() -> dict:
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def make_icon(on: bool) -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (80, 200, 80) if on else (120, 120, 120)
    # monitor frame
    draw.rectangle([8, 8, 56, 44], outline=color, width=4)
    # stand
    draw.rectangle([28, 44, 36, 54], fill=color)
    draw.rectangle([20, 54, 44, 58], fill=color)
    return img


def is_autostart_enabled() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def set_autostart(enabled: bool):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0, winreg.KEY_SET_VALUE)
    if enabled:
        exe = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe}"')
    else:
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass
    winreg.CloseKey(key)


class App:
    def __init__(self):
        self._config = load_config()
        self._tray = None

        self._mqtt = MqttClient(
            self._config,
            on_turn_on=self._handle_turn_on,
            on_turn_off=self._handle_turn_off,
        )

    def _handle_turn_on(self):
        scr.turn_on()
        self._mqtt.publish_state(True)
        self._refresh_tray()

    def _handle_turn_off(self):
        scr.turn_off()
        self._mqtt.publish_state(False)
        self._refresh_tray()

    def _refresh_tray(self):
        if self._tray:
            self._tray.icon = make_icon(scr.is_on())
            self._tray.update_menu()

    def _build_menu(self):
        on = scr.is_on()
        autostart = is_autostart_enabled()
        return pystray.Menu(
            pystray.MenuItem(f"Screen: {'EIN' if on else 'AUS'}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Screen einschalten", lambda: self._handle_turn_on()),
            pystray.MenuItem("Screen ausschalten", lambda: self._handle_turn_off()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Autostart aktivieren" if not autostart else "Autostart deaktivieren",
                lambda: set_autostart(not autostart),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Beenden", lambda: self._tray.stop()),
        )

    def run(self):
        self._mqtt.start()
        self._tray = pystray.Icon(
            APP_NAME,
            icon=make_icon(scr.is_on()),
            title="SOOHA – Screen Off Over Home Assistant",
            menu=pystray.Menu(lambda: self._build_menu()),
        )
        self._tray.run()


if __name__ == "__main__":
    App().run()
