import ctypes
import ctypes.wintypes
from version import __version__

_GetTickCount64 = ctypes.windll.kernel32.GetTickCount64
_GetTickCount64.restype = ctypes.c_ulonglong


def windows_uptime_str() -> str:
    ms = _GetTickCount64()
    total_sec = ms // 1000
    days, rem  = divmod(total_sec, 86400)
    hours, rem = divmod(rem, 3600)
    minutes    = rem // 60
    if days:
        return f"{days}d {hours}h {minutes:02d}m"
    return f"{hours}h {minutes:02d}m"


def sooha_version() -> str:
    return f"v{__version__}"


def cpu_percent() -> float:
    try:
        import psutil
        return round(psutil.cpu_percent(interval=0.5), 1)
    except Exception:
        return 0.0


def ram_percent() -> float:
    try:
        import psutil
        return round(psutil.virtual_memory().percent, 1)
    except Exception:
        return 0.0


