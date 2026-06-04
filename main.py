import pygame
import os
import sys
import ctypes
import ctypes.wintypes

# BASE_DIR = main.py 所在的文件夹
# sys._MEIPASS 是 PyInstaller 打包后解压资源的临时文件夹
# 没打包时 sys._MEIPASS 不存在，就用 __file__ 的目录
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(__file__))#这句话的意思是：如果 sys 模块有 _MEIPASS 属性（打包后才有），就用它；否则用 __file__ 的目录。这样无论是打包后还是直接运行，程序都能正确找到资源文件夹。

# 在调用 SetWindowPos 之前声明参数类型
ctypes.windll.user32.SetWindowPos.argtypes = [
    ctypes.c_void_p,   # HWND
    ctypes.c_void_p,   # HWND hWndInsertAfter
    ctypes.c_int,      # int X
    ctypes.c_int,      # int Y
    ctypes.c_int,      # int cx
    ctypes.c_int,      # int cy
    ctypes.c_uint,     # UINT uFlags
]

def any_key_down():
    """
    检测"当前是否有任意键被按着"。

    用 Windows 的 GetAsyncKeyState 来读键盘状态。
    和 BongoCat 的 GetKeyState 一样，都是系统级 API——
    不管 Pygame 窗口有没有焦点，都能读到按键。

    & 0x8000 的意思是：只检查最高位。
    最高位 = 1 → 键正被按着
    最高位 = 0 → 键没被按着 测试

    遍历所有虚拟键码（1 到 254），只要有一个被按着就返回 True。
    """
    for vk in range(1, 255):
        if ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000:
            return True
    return False

def get_window_position(hwnd):
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top

def main():
    # ---- 初始化 Pygame ----
    os.environ["SDL_IME_SHOW_UI"] = "0"  # 禁用输入法，确保 WASD 等字母键能被检测
    pygame.init()
    pygame.key.stop_text_input()          # 额外保险：停止文本输入模式

    #---- 创建窗口 ----
    screen = pygame.display.set_mode((400, 300), pygame.NOFRAME)  # 无边框窗口
    hwnd=pygame.display.get_wm_info()['window']  # 获取窗口句柄
    ctypes.windll.user32.SetWindowLongW(hwnd,-20, ctypes.windll.user32.GetWindowLongW(hwnd,-20) | 0x00080000)  # 设置窗口为工具窗口（WS_EX_TOOLWINDOW）和透明（WS_EX_TRANSPARENT）
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd,0xff00ff,0,1)
    #透明窗口

    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
    #悬浮窗口，参数 -1 = HWND_TOPMOST，0,0 = 不改变位置，0,0 = 不改变大小，0x0001 | 0x0002 = SWP_NOSIZE | SWP_NOMOVE

    pygame.display.set_caption("自嘲熊")
    clock = pygame.time.Clock()

    # ---- 加载图片 ----
    # 三张图对应三种状态：
    #   image_0 = idle  （待机，右手在上，左手在下）
    #   image_1 = left  （中间态，左右手都在中间）
    #   image_2 = right （右手在下，左手在上）
    res = os.path.join(BASE_DIR, "resourse")
    begin = pygame.image.load(os.path.join(res, "bear_frame_0.png")).convert_alpha()
    middle = pygame.image.load(os.path.join(res, "bear_frame_1.png")).convert_alpha()
    end = pygame.image.load(os.path.join(res, "bear_frame_2.png")).convert_alpha()

    # ---- 状态变量 ----
    # 这些变量"跨帧存活"——它们的值从上一帧保留到下一帧，
    # 不随循环重新开始而重置。这就是程序的"记忆"。
    timer = 0              # 动画还要显示多少帧。0 = 待机
    key_was_down = False   # 上一帧是否有人按着键（用于边沿检测）
    dragging = False    # 是否正在拖拽

    running = True
    while running:
        # ============================================================
        # ① 处理事件（只管关闭窗口）
        # ============================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # 2 处理事件（鼠标拖拽）
            if event.type == pygame.MOUSEBUTTONDOWN:
                pt = ctypes.wintypes.POINT()
                #把pt定义为C语言的变量，在C语言中point有x和y两个属性
                ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                #ctypes.windll.user32.GetCursorPos，这里可以获得鼠标的xy坐标，然后传输进pt
                dragging=True
                mouse_x, mouse_y = pt.x, pt.y
                window_x, window_y = get_window_position(hwnd)
                print(f"检测到鼠标按下，位置: ({window_x}, {window_y})")

            elif event.type == pygame.MOUSEMOTION and dragging:
                pt = ctypes.wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                dx= pt.x - mouse_x
                dy= pt.y - mouse_y
                #窗口也移动
                new_window_x=window_x + dx
                new_window_y=window_y + dy
                ctypes.windll.user32.SetWindowPos(hwnd, 0, new_window_x, new_window_y, 0, 0, 0x0001 | 0x0004)
                window_x, window_y = new_window_x, new_window_y
                mouse_x, mouse_y = pt.x, pt.y
                print(f"检测到鼠标移动，窗口新位置: ({new_window_x}, {new_window_y})")

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging=False



        # ============================================================
        # ② 边沿检测：检测"刚按下"的瞬间
        #    刚按下 = 这一帧按着 AND 上一帧没按
        #    和 BongoCat 的 last_state + state 是同一个逻辑
        # ============================================================
        key_is_down = any_key_down()

        if key_is_down and not key_was_down:   # ← "刚按下"的瞬间
            timer = 12                             # 启动动画（30帧 ≈ 0.5秒）
        key_was_down = key_is_down  # 把这帧的状态存起来，给下一帧的"上一帧"用

        # ============================================================
        # ③ 计时器：每帧减 1，自然衰减到 0
        # ============================================================
        if timer > 0:
            timer -= 1

        # ============================================================
        # ④ 根据 timer 阶段画图（三段式动画）
        #    timer 30→21  第一阶段：middle（手从待机位出发）
        #    timer 20→11  第二阶段：end   （手到达最底/最高）
        #    timer 10→1   第三阶段：middle（手回弹到中间）
        #    timer = 0    结束：   begin （回到待机位）
        #
        #    三张图分别对应：
        #    begin  = 右手在上，左手在下（待机位）
        #    middle = 双手都在中间
        #    end    = 右手在下，左手在上（和待机相反）
        # ============================================================
        screen.fill((255, 0, 255))  # 填充背景色（纯红，后面会被透明掉）

        # 居中：窗口中央 - 图片一半 = 图片左上角该放的位置
        x = screen.get_width() // 2 - begin.get_width() // 2
        y = screen.get_height() // 2 - begin.get_height() // 2

        if timer > 9:
            screen.blit(middle, (x, y))
        elif timer > 4:
            screen.blit(end, (x, y))
        elif timer > 0:
            screen.blit(middle, (x, y))
        else:
            screen.blit(begin, (x, y))

        # ============================================================
        # ⑤ 翻到屏幕前 + 限制帧率
        # ============================================================
        pygame.display.flip()
        clock.tick(80)
        #clock.tick()把一秒分成了X帧，然后前面用time控制显示的帧数，以此决定显示画面的停留时间
    pygame.quit()


if __name__ == "__main__":
    main()
