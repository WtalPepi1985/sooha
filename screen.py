import ctypes
import threading
import time

_state = True
_turned_off_at_tick = 0

WM_SYSCOMMAND = 0x0112
SC_MONITORPOWER = 0xF170


class _LastInputInfo(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


def _desktop():
    return ctypes.windll.user32.GetDesktopWindow()


def _tick() -> int:
    return ctypes.windll.kernel32.GetTickCount()


def _last_input_tick() -> int:
    lii = _LastInputInfo()
    lii.cbSize = ctypes.sizeof(_LastInputInfo)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    return lii.dwTime


def turn_off():
    """Turn off monitor. Runs with a short delay so the triggering click doesn't immediately wake it."""
    global _state, _turned_off_at_tick
    _state = False

    def _do():
        global _turned_off_at_tick
        time.sleep(0.5)
        ctypes.windll.user32.SendMessageW(_desktop(), WM_SYSCOMMAND, SC_MONITORPOWER, 2)
        _turned_off_at_tick = _tick()

    threading.Thread(target=_do, daemon=True).start()


def turn_on():
    global _state
    ctypes.windll.user32.SendMessageW(_desktop(), WM_SYSCOMMAND, SC_MONITORPOWER, -1)
    _state = True


def check_woken() -> bool:
    """Returns True if user input woke the screen since we turned it off. Updates state."""
    global _state
    if _state:
        return False
    if _last_input_tick() > _turned_off_at_tick:
        _state = True
        return True
    return False


def is_on() -> bool:
    return _state
