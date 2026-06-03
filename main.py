import pygame
import os
import ctypes

# BASE_DIR = main.py 所在的文件夹
# 之后加载图片都用相对这个文件夹的路径，这样程序搬到哪都能跑
BASE_DIR = os.path.dirname(__file__)


def any_key_down():
    """
    检测"当前是否有任意键被按着"。

    用 Windows 的 GetAsyncKeyState 来读键盘状态。
    和 BongoCat 的 GetKeyState 一样，都是系统级 API——
    不管 Pygame 窗口有没有焦点，都能读到按键。

    & 0x8000 的意思是：只检查最高位。
    最高位 = 1 → 键正被按着
    最高位 = 0 → 键没被按着

    遍历所有虚拟键码（1 到 254），只要有一个被按着就返回 True。
    """
    for vk in range(1, 255):
        if ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000:
            return True
    return False


def main():
    # ---- 初始化 Pygame ----
    os.environ["SDL_IME_SHOW_UI"] = "0"  # 禁用输入法，确保 WASD 等字母键能被检测
    pygame.init()
    pygame.key.stop_text_input()          # 额外保险：停止文本输入模式
    screen = pygame.display.set_mode((400, 300))
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
    current_paw = None      # "left" 或 "right"，记录本轮是哪只手在按
    press_count = 0         # 总共敲了多少次键。奇数→左手，偶数→右手
    key_was_down = False   # 上一帧是否有人按着键（用于边沿检测）

    running = True
    while running:
        # ============================================================
        # ① 处理事件（只管关闭窗口）
        # ============================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ============================================================
        # ② 边沿检测：检测"刚按下"的瞬间
        #    刚按下 = 这一帧按着 AND 上一帧没按
        #    和 BongoCat 的 last_state + state 是同一个逻辑
        # ============================================================
        key_is_down = any_key_down()

        if key_is_down and not key_was_down:   # ← "刚按下"的瞬间
            press_count += 1                       # 敲键次数 +1
            timer = 12                             # 启动动画（30帧 ≈ 0.5秒）
            if press_count % 2 == 1:               # 奇数次 → 左手主导
                current_paw = "left"
            else:                                  # 偶数次 → 右手主导
                current_paw = "right"

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
        screen.fill((240, 240, 240))

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
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
