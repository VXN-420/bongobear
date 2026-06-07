import pystray
from PIL import Image
import ctypes
import threading
import os
import sys

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(__file__))


def create_tray(hwnd): 
    icon_path = os.path.join(BASE_DIR, "resourse", "bear_frame_0.png")
    icon_img = Image.open(icon_path)

    def on_toggle(icon, item):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            ctypes.windll.user32.ShowWindow(hwnd, 0)
        else:
            ctypes.windll.user32.ShowWindow(hwnd, 5)

    def on_quit(icon, item):
        icon.stop()
        os._exit(0)  # 直接退出整个程序

    menu = pystray.Menu(
        pystray.MenuItem("显示/隐藏", on_toggle),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("退出", on_quit),
    )

    icon = pystray.Icon("自嘲熊", icon_img, "自嘲熊", menu)
    t = threading.Thread(target=icon.run, daemon=True)
    t.start()
    return icon