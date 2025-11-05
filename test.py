import ctypes
import time
from ctypes import wintypes

# ULONG_PTR зависит от разрядности системы
if ctypes.sizeof(ctypes.c_void_p) == 8:  # 64-bit
    ULONG_PTR = ctypes.c_ulonglong
else:  # 32-bit
    ULONG_PTR = ctypes.c_ulong

VK_DELETE = 0x2E
KEYEVENTF_KEYUP = 0x0002
INPUT_KEYBOARD = 1

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class _INPUTunion(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT)]

class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTunion)]

SendInput = ctypes.windll.user32.SendInput

def press_delete():
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.ki.wVk = VK_DELETE
    inp.ki.wScan = 0
    inp.ki.dwFlags = 0
    inp.ki.time = 0
    inp.ki.dwExtraInfo = 0
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

    time.sleep(0.02)

    inp.ki.dwFlags = KEYEVENTF_KEYUP
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    print("Delete нажат")

if __name__ == "__main__":
    print("Переключись на рабочий стол и выдели файл. Через 2 сек будет Delete.")
    time.sleep(2)
    press_delete()
