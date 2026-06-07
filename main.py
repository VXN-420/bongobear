import pygame
import os
import sys
import ctypes
import ctypes.wintypes
from tray import create_tray

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(__file__))

ctypes.windll.user32.SetWindowPos.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_uint,
]

SCALE = 1.0  # 当前缩放比例，右键拖拽时改变


def any_key_down():
    """遍历所有虚拟键码（1 到 254），只要有一个被按着就返回 True。"""
    for vk in range(1, 255):
        if ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000:
            return True
    return False


def get_window_position(hwnd):
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top


def rescale_images(raw_begin, raw_middle, raw_end):
    """从缓存的原始图片按当前 SCALE 缩放，不读硬盘"""
    w = int(raw_begin.get_width() * SCALE)
    h = int(raw_begin.get_height() * SCALE)
    begin = pygame.transform.scale(raw_begin, (w, h))
    middle = pygame.transform.scale(raw_middle, (w, h))
    end = pygame.transform.scale(raw_end, (w, h))
    return begin, middle, end


def main():
    global SCALE

    os.environ["SDL_IME_SHOW_UI"] = "0"
    pygame.init()
    pygame.key.stop_text_input()

    # ---- 创建窗口（大小固定不变）----
    screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)

    icon = pygame.image.load(os.path.join(BASE_DIR, "resourse", "bear_frame_0.png")).convert_alpha()
    pygame.display.set_icon(icon)

    hwnd = pygame.display.get_wm_info()['window']
    ctypes.windll.user32.SetWindowLongW(hwnd, -20,
        ctypes.windll.user32.GetWindowLongW(hwnd, -20) | 0x00080000)
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0xff00ff, 0, 1)
    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)

    pygame.display.set_caption("自嘲熊")
    clock = pygame.time.Clock()

    # ---- 加载原始图片（缓存，永远不缩放）----
    res = os.path.join(BASE_DIR, "resourse")
    raw_begin = pygame.image.load(os.path.join(res, "bear_frame_0.png")).convert_alpha()
    raw_middle = pygame.image.load(os.path.join(res, "bear_frame_1.png")).convert_alpha()
    raw_end = pygame.image.load(os.path.join(res, "bear_frame_2.png")).convert_alpha()

    # ---- 首次按 SCALE 缩放 ----
    begin, middle, end = rescale_images(raw_begin, raw_middle, raw_end)

    # ---- 系统托盘 ----
    tray_icon = create_tray(hwnd)

    # ---- 状态变量 ----
    timer = 0
    key_was_down = False
    # 左键拖拽
    dragging = False
    mouse_was_down = False
    mouse_start_x = 0
    mouse_start_y = 0
    window_start_x = 0
    window_start_y = 0
    # 右键缩放
    scaling = False
    right_was_down = False
    scale_start = 1.0
    mouse_scale_start_x = 0

    running = True
    while running:
        # ---- 每帧拿一次鼠标位置 ----
        pt = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))

        # ---- ① 处理事件 ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ---- ② 左键拖拽 ----
        mouse_is_down = ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000

        if mouse_is_down and not mouse_was_down:
            bx = screen.get_width() // 2 - begin.get_width() // 2
            by = screen.get_height() // 2 - begin.get_height() // 2
            win_x, win_y = get_window_position(hwnd)
            if win_x + bx <= pt.x < win_x + bx + begin.get_width() and \
               win_y + by <= pt.y < win_y + by + begin.get_height():
                dragging = True
                mouse_start_x, mouse_start_y = pt.x, pt.y
                window_start_x, window_start_y = win_x, win_y

        elif mouse_is_down and dragging:
            dx = pt.x - mouse_start_x
            dy = pt.y - mouse_start_y
            new_x = window_start_x + dx
            new_y = window_start_y + dy
            ctypes.windll.user32.SetWindowPos(hwnd, 0, new_x, new_y, 0, 0, 0x0001 | 0x0004)

        else:
            dragging = False

        mouse_was_down = mouse_is_down

        # ---- ③ 右键缩放 ----
        right_is_down = ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000

        if right_is_down and not right_was_down:
            bx = screen.get_width() // 2 - begin.get_width() // 2
            by = screen.get_height() // 2 - begin.get_height() // 2
            win_x, win_y = get_window_position(hwnd)
            if win_x + bx <= pt.x < win_x + bx + begin.get_width() and \
               win_y + by <= pt.y < win_y + by + begin.get_height():
                scaling = True
                scale_start = SCALE
                mouse_scale_start_x = pt.x

        elif right_is_down and scaling:
            dx = pt.x - mouse_scale_start_x
            SCALE = scale_start + dx * 0.005
            if SCALE < 0.3:
                SCALE = 0.3
            if SCALE > 3.0:
                SCALE = 3.0
            # 只重缩放图片，不碰窗口
            begin, middle, end = rescale_images(raw_begin, raw_middle, raw_end)

        else:
            scaling = False

        right_was_down = right_is_down

        # ---- ④ 按键边沿检测 ----
        key_is_down = any_key_down()

        if key_is_down and not key_was_down:
            timer = 12
        key_was_down = key_is_down

        # ---- ⑤ 计时器 ----
        if timer > 0:
            timer -= 1

        # ---- ⑥ 画图 ----
        screen.fill((255, 0, 255))

        x = screen.get_width() // 2 - begin.get_width() // 2
        y = screen.get_height() // 2 - begin.get_height() // 2

        if timer > 8:
            screen.blit(middle, (x, y))
        elif timer > 4:
            screen.blit(end, (x, y))
        elif timer > 0:
            screen.blit(middle, (x, y))
        else:
            screen.blit(begin, (x, y))

        pygame.display.flip()
        clock.tick(80)

    tray_icon.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
