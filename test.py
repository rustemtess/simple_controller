import ctypes
import time

# === Настройки ===
time.sleep(3)  # 3 секунды, чтобы успеть навести Chrome

# Получаем размер экрана
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Координаты кнопки "Закрыть вкладку" (примерно правый верхний угол окна)
# можно подстроить под свой монитор
x = screen_width - 60
y = 20

# Устанавливаем позицию курсора
ctypes.windll.user32.SetCursorPos(x, y)

# Клик левой кнопкой мыши (down + up)
ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # ЛКМ нажата
time.sleep(0.05)
ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # ЛКМ отпущена
