import ctypes
import time

def hold_left_click(duration=3):
    """Удерживает левую кнопку мыши указанное количество секунд"""
    # Нажать левую кнопку мыши
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
    # Ждать указанное время
    time.sleep(duration)
    # Отпустить левую кнопку мыши
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)

# --- пример использования ---
hold_left_click(3)  # удерживаем 3 секунды
