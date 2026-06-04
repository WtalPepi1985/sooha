import ctypes

_state = True  # assume screen is on at startup

SC_MONITORPOWER = 0xF170
WM_SYSCOMMAND = 0x0112
HWND_BROADCAST = -1


def turn_off():
    global _state
    ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2)
    _state = False


def turn_on():
    global _state
    ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, -1)
    _state = True


def is_on() -> bool:
    return _state
