import os
import sys
import time
import threading
import winreg

import pystray
from PIL import Image, ImageDraw

import config as cfg
import screen as scr
from mqtt_client import MqttClient
from settings import SettingsWindow

AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "SOOHA"

HA_CHECK_INTERVAL = 300   # seconds between HA update checks
TOOLTIP_INTERVAL  = 30    # seconds between tooltip refreshes


def make_icon(on: bool) -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (80, 200, 80) if on else (120, 120, 120)
    draw.rectangle([8, 8, 56, 44], outline=color, width=4)
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
        self._config = cfg.load()
        self._tray = None
        self._start_time = time.time()
        self._pending_updates: list = []
        self._settings_win = SettingsWindow(on_saved=self._on_settings_saved)

        self._mqtt = MqttClient(
            self._config,
            on_turn_on=self._handle_turn_on,
            on_turn_off=self._handle_turn_off,
        )
        self._ha = self._make_ha_client()

    def _make_ha_client(self):
        from ha_client import HaClient
        url = self._config.get("ha_url", "")
        token = self._config.get("ha_token", "")
        if url and token:
            return HaClient(url, token)
        return None

    # ── Screen handlers ───────────────────────────────────────────────────────

    def _handle_turn_on(self):
        scr.turn_on()
        self._mqtt.publish_state(True)
        self._refresh_tray()

    def _handle_turn_off(self):
        scr.turn_off()
        self._mqtt.publish_state(False)
        self._refresh_tray()

    # ── Tray ──────────────────────────────────────────────────────────────────

    def _refresh_tray(self):
        if self._tray:
            self._tray.icon = make_icon(scr.is_on())
            self._tray.update_menu()
            self._update_tooltip()

    def _runtime_str(self) -> str:
        elapsed = int(time.time() - self._start_time)
        h, m = divmod(elapsed // 60, 60)
        return f"{h}h {m:02d}m"

    def _update_tooltip(self):
        if not self._tray:
            return
        c = self._config
        parts = [f"Screen: {'EIN' if scr.is_on() else 'AUS'}"]
        if c.get("feature_runtime"):
            parts.append(f"Laufzeit: {self._runtime_str()}")
        if c.get("feature_mqtt_status"):
            parts.append(f"MQTT: {'✓' if self._mqtt.is_connected() else '✗'}")
        if c.get("feature_update_notify") and self._pending_updates:
            parts.append(f"Updates: {len(self._pending_updates)} verfügbar")
        self._tray.title = "SOOHA  |  " + "  ·  ".join(parts)

    def _build_menu(self):
        c = self._config
        on = scr.is_on()
        autostart = is_autostart_enabled()

        items = [
            pystray.MenuItem(f"Screen: {'EIN' if on else 'AUS'}", None, enabled=False),
        ]

        # Update hint — only show when pending updates exist
        if c.get("feature_update_notify") and self._pending_updates:
            items.append(pystray.MenuItem(
                f"⚠ {len(self._pending_updates)} Update(s) verfügbar", None, enabled=False
            ))

        items += [
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Screen einschalten",  lambda: self._handle_turn_on()),
            pystray.MenuItem("Screen ausschalten",  lambda: self._handle_turn_off()),
            pystray.Menu.SEPARATOR,
        ]

        if c.get("feature_reboot"):
            items.append(pystray.MenuItem(
                "Windows neu starten…",
                lambda: threading.Thread(target=self._reboot, daemon=True).start(),
            ))
            items.append(pystray.Menu.SEPARATOR)

        items += [
            pystray.MenuItem(
                "Autostart aktivieren" if not autostart else "Autostart deaktivieren",
                lambda: set_autostart(not autostart),
            ),
            pystray.MenuItem("Einstellungen…", lambda: self._settings_win.open()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Beenden", lambda: self._tray.stop()),
        ]

        return pystray.Menu(*items)

    # ── Reboot ────────────────────────────────────────────────────────────────

    def _reboot(self):
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        if messagebox.askyesno("Windows neu starten", "Wirklich jetzt neu starten?", parent=root):
            os.system("shutdown /r /t 0")
        root.destroy()

    # ── Settings callback ─────────────────────────────────────────────────────

    def _on_settings_saved(self, new_config: dict):
        self._config = new_config
        self._ha = self._make_ha_client()
        self._update_tooltip()

    # ── Background threads ────────────────────────────────────────────────────

    def _woken_watcher(self):
        """Polls every 2s whether user input woke the screen, syncs state + HA."""
        while True:
            time.sleep(2)
            if scr.check_woken():
                self._mqtt.publish_state(True)
                self._refresh_tray()

    def _ticker(self):
        last_ha_check = 0.0
        while True:
            time.sleep(TOOLTIP_INTERVAL)
            self._update_tooltip()
            if self._ha and self._config.get("feature_update_notify"):
                if time.time() - last_ha_check >= HA_CHECK_INTERVAL:
                    self._pending_updates = self._ha.get_pending_updates()
                    last_ha_check = time.time()
                    self._update_tooltip()
                    self._tray.update_menu()

    # ── Entry point ───────────────────────────────────────────────────────────

    def run(self):
        self._mqtt.start()
        threading.Thread(target=self._ticker, daemon=True).start()
        threading.Thread(target=self._woken_watcher, daemon=True).start()

        self._tray = pystray.Icon(
            APP_NAME,
            icon=make_icon(scr.is_on()),
            title="SOOHA",
            menu=pystray.Menu(lambda: self._build_menu()),
        )
        self._update_tooltip()
        self._tray.run()


if __name__ == "__main__":
    App().run()
