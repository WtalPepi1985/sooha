import threading
import tkinter as tk
from tkinter import messagebox, ttk

import config as cfg

BG = "#1e1e1e"
BG2 = "#2d2d2d"
BG3 = "#3c3c3c"
FG = "#cccccc"
FG_DIM = "#666666"
ACCENT = "#0078d4"
GREEN = "#107c10"


class SettingsWindow:
    def __init__(self, on_saved=None):
        self._on_saved = on_saved
        self._root = None

    def open(self):
        if self._root and self._root.winfo_exists():
            self._root.lift()
            self._root.focus_force()
            return
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        self._root = tk.Tk()
        self._root.title("SOOHA – Einstellungen")
        self._root.configure(bg=BG)
        self._root.resizable(False, False)
        self._build_ui(cfg.load())
        self._root.mainloop()

    def _apply_style(self):
        s = ttk.Style(self._root)
        s.theme_use("clam")
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG2, foreground=FG, padding=[14, 5])
        s.map("TNotebook.Tab", background=[("selected", BG3)], foreground=[("selected", "#ffffff")])
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=FG)
        s.configure("TEntry", fieldbackground=BG2, foreground="#ffffff", insertcolor="#ffffff", bordercolor=BG3)
        s.configure("TCheckbutton", background=BG, foreground=FG)
        s.map("TCheckbutton", background=[("active", BG)], foreground=[("active", "#ffffff")])

    def _build_ui(self, data: dict):
        self._apply_style()
        root = self._root

        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True, padx=16, pady=(14, 8))

        # ── MQTT Tab ─────────────────────────────────────────────────────────
        f_mqtt = ttk.Frame(nb)
        nb.add(f_mqtt, text="  MQTT  ")

        self._mqtt_host = self._row(f_mqtt, "Host", data["mqtt_host"], 0)
        self._mqtt_port = self._row(f_mqtt, "Port", str(data["mqtt_port"]), 1, width=8)
        self._mqtt_user = self._row(f_mqtt, "Benutzername", data["mqtt_username"], 2)
        self._mqtt_pass = self._row(f_mqtt, "Passwort", data["mqtt_password"], 3, secret=True)
        self._device_name = self._row(f_mqtt, "Gerätename", data["device_name"], 4)
        self._device_id = self._row(f_mqtt, "Geräte-ID", data["device_id"], 5)

        self._btn(f_mqtt, "Verbindung testen", self._test_mqtt, ACCENT).grid(
            row=6, column=1, sticky="w", padx=8, pady=(14, 8)
        )

        # ── Home Assistant Tab ────────────────────────────────────────────────
        f_ha = ttk.Frame(nb)
        nb.add(f_ha, text="  Home Assistant  ")

        self._ha_url = self._row(f_ha, "URL", data["ha_url"], 0, width=34)
        self._ha_token = self._row(f_ha, "Token", data["ha_token"], 1, secret=True, width=34)

        self._btn(f_ha, "Verbindung testen", self._test_ha, ACCENT).grid(
            row=2, column=1, sticky="w", padx=8, pady=(14, 8)
        )

        # ── Features Tab ─────────────────────────────────────────────────────
        f_feat = ttk.Frame(nb)
        nb.add(f_feat, text="  Features  ")

        features = [
            ("feature_update_notify", "Update-Benachrichtigung", "HA-Updates werden im Tray-Tooltip angezeigt"),
            ("feature_runtime",       "Laufzeit anzeigen",       "App-Laufzeit im Tray-Tooltip"),
            ("feature_reboot",        "Reboot-Option",           "\"Windows neu starten\" im Tray-Menü (mit Bestätigung)"),
            ("feature_mqtt_status",   "MQTT-Status anzeigen",    "Verbindungsstatus im Tray-Tooltip"),
        ]
        self._feat_vars: dict[str, tk.BooleanVar] = {}
        for i, (key, label, hint) in enumerate(features):
            var = tk.BooleanVar(value=data[key])
            self._feat_vars[key] = var
            row = i * 2
            ttk.Checkbutton(f_feat, text=label, variable=var).grid(
                row=row, column=0, sticky="w", padx=14, pady=(10, 0)
            )
            ttk.Label(f_feat, text=f"    {hint}", foreground=FG_DIM).grid(
                row=row + 1, column=0, sticky="w", padx=14, pady=(0, 2)
            )

        # ── Bottom buttons ────────────────────────────────────────────────────
        bar = tk.Frame(root, bg=BG)
        bar.pack(fill="x", padx=16, pady=(4, 14))

        self._btn(bar, "Speichern", self._save, GREEN).pack(side="right", padx=(4, 0))
        self._btn(bar, "Abbrechen", self._root.destroy, BG2).pack(side="right")

    def _row(self, parent, label: str, value: str, row: int, secret=False, width=24):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="e", padx=(14, 6), pady=7)
        var = tk.StringVar(value=value)
        ttk.Entry(parent, textvariable=var, width=width, show="●" if secret else "").grid(
            row=row, column=1, sticky="w", padx=(0, 14), pady=7
        )
        return var

    def _btn(self, parent, text: str, cmd, bg: str) -> tk.Button:
        return tk.Button(
            parent, text=text, command=cmd,
            bg=bg, fg="white", activebackground=bg, activeforeground="white",
            relief="flat", padx=14, pady=5, cursor="hand2", bd=0,
        )

    # ── Connection tests ──────────────────────────────────────────────────────

    def _test_mqtt(self):
        import paho.mqtt.client as mqtt_lib

        result = {"ok": False, "msg": ""}
        done = threading.Event()

        def on_connect(client, userdata, flags, rc):
            result["ok"] = rc == 0
            result["msg"] = "Verbunden!" if rc == 0 else f"Fehler (RC {rc})"
            client.disconnect()
            done.set()

        c = mqtt_lib.Client(client_id="sooha-test")
        if self._mqtt_user.get():
            c.username_pw_set(self._mqtt_user.get(), self._mqtt_pass.get())
        c.on_connect = on_connect
        try:
            c.connect(self._mqtt_host.get(), int(self._mqtt_port.get()), keepalive=5)
            c.loop_start()
            done.wait(timeout=5)
            c.loop_stop()
        except Exception as e:
            result["msg"] = str(e)

        if result["ok"]:
            messagebox.showinfo("MQTT Test", result["msg"], parent=self._root)
        else:
            messagebox.showerror("MQTT Test", result["msg"] or "Timeout – kein Broker erreichbar", parent=self._root)

    def _test_ha(self):
        import requests as req
        url = self._ha_url.get().rstrip("/") + "/api/"
        try:
            r = req.get(url, headers={"Authorization": f"Bearer {self._ha_token.get()}"}, timeout=5)
            if r.status_code == 200:
                ver = r.json().get("version", "?")
                messagebox.showinfo("HA Test", f"Verbunden!\nHome Assistant {ver}", parent=self._root)
            else:
                messagebox.showerror("HA Test", f"HTTP {r.status_code}", parent=self._root)
        except Exception as e:
            messagebox.showerror("HA Test", str(e), parent=self._root)

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save(self):
        try:
            port = int(self._mqtt_port.get())
        except ValueError:
            messagebox.showerror("Fehler", "Port muss eine Zahl sein.", parent=self._root)
            return

        data = {
            "mqtt_host":             self._mqtt_host.get().strip(),
            "mqtt_port":             port,
            "mqtt_username":         self._mqtt_user.get(),
            "mqtt_password":         self._mqtt_pass.get(),
            "device_name":           self._device_name.get().strip(),
            "device_id":             self._device_id.get().strip(),
            "ha_url":                self._ha_url.get().strip().rstrip("/"),
            "ha_token":              self._ha_token.get(),
            **{k: v.get() for k, v in self._feat_vars.items()},
        }
        cfg.save(data)
        if self._on_saved:
            self._on_saved(data)
        messagebox.showinfo("Gespeichert", "Einstellungen gespeichert.\nNeustart empfohlen.", parent=self._root)
        self._root.destroy()
