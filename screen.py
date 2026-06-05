import ctypes
import ctypes.wintypes
import threading
import time

_state = True
_turned_off_at_tick = 0

WM_SYSCOMMAND  = 0x0112
SC_MONITORPOWER = 0xF170
HWND_BROADCAST  = 0xFFFF  # correct value — NOT -1

# Explicit argtypes prevent silent type-conversion bugs
_user32 = ctypes.windll.user32

_SendMessage = _user32.SendMessageW
_SendMessage.restype  = ctypes.c_long
_SendMessage.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_ulong, ctypes.c_long]

_PostMessage = _user32.PostMessageW
_PostMessage.restype  = ctypes.wintypes.BOOL
_PostMessage.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_ulong, ctypes.c_long]

_GetDesktopWindow = _user32.GetDesktopWindow
_GetDesktopWindow.restype = ctypes.c_void_p

_GetTickCount64 = ctypes.windll.kernel32.GetTickCount64
_GetTickCount64.restype = ctypes.c_ulonglong

# mouse_event for waking the monitor (deprecated but simpler than SendInput; still works on all Windows versions)
_mouse_event = _user32.mouse_event
_mouse_event.restype  = None
_mouse_event.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]

MOUSEEVENTF_MOVE = 0x0001


class _LastInputInfo(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


def _last_input_tick() -> int:
    lii = _LastInputInfo()
    lii.cbSize = ctypes.sizeof(_LastInputInfo)
    _user32.GetLastInputInfo(ctypes.byref(lii))
    return lii.dwTime


def _tick() -> int:
    # GetTickCount64 is 64-bit, GetLastInputInfo is 32-bit — mask to match
    return _GetTickCount64() & 0xFFFFFFFF


def turn_off():
    global _state, _turned_off_at_tick
    _state = False

    def _do():
        global _turned_off_at_tick
        time.sleep(0.5)  # let the triggering click finish before sending
        desktop = _GetDesktopWindow()
        _SendMessage(desktop, WM_SYSCOMMAND, SC_MONITORPOWER, 2)
        _PostMessage(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2)
        _turned_off_at_tick = _tick()

    threading.Thread(target=_do, daemon=True).start()


def turn_on():
    global _state
    # A tiny mouse nudge is needed to wake a monitor that's in hardware sleep —
    # SC_MONITORPOWER=-1 alone doesn't always trigger the display driver.
    _mouse_event(MOUSEEVENTF_MOVE, 1, 0, 0, 0)
    _SendMessage(_GetDesktopWindow(), WM_SYSCOMMAND, SC_MONITORPOWER, -1)
    _state = True


def check_woken() -> bool:
    """Returns True (and updates state) if input woke the screen since we turned it off."""
    global _state
    if _state:
        return False
    if _last_input_tick() > _turned_off_at_tick:
        _state = True
        return True
    return False


def is_on() -> bool:
    return _state
