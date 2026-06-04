import pygame
import os
import sys
import ctypes

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
#1.os.path.dirname(__file__) 获取当前脚本所在的目录（不包括文件名）

#第一部分，检测按键
def any_key_down():
    for key in range(1,255):
        if ctypes.windll.user32.GetAsyncKeyState(key) & 0x8000:
        #GetAsyncKeyState函数用于检测指定的键是否被按下。
        # 它返回一个16位数，其中最高位（0x8000））第16位）是否为1表示该键是否被按下。
        # 0x8000它表示第16位为1的，其余位为0
        # &运算符用于检查两个数的对应位是否都为1，如果是，则结果的对应位为1，否则为0。
            return True
    return False

#第二部分，主程序
def main():
    os.environ['SDL_VIDEO_WINDOW_UI'] = '0'
    pygame.init()#初始化pygame库
    pygame.key.stop_text_input()#禁用文本输入功能
    screen=pygame.display.set_mode((400,300))#设置窗口大小为400x300像素
    clock = pygame.time.Clock()#创建一个时钟对象，用于控制游戏循环的帧率


    #————————图片——————
    res= os.path.join(BASE_DIR, 'resourse')#获取资源文件夹的路径
    begin =pygame.image.load(os.path.join(res,"bear_frame_0.png")).convert_alpha()
    middle = pygame.image.load(os.path.join(res, "bear_frame_1.png")).convert_alpha()
    end = pygame.image.load(os.path.join(res, "bear_frame_2.png")).convert_alpha()
    #.convert_alpha()的作用是将图片转换为适合当前显示设备的格式，同时保留 PNG 的透明度信息，从而获得正确显示和更高的渲染性能。

    #——状态变量——
    time=0
    key_was_down=False

    #----event loop----
    running=True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    #----状态更新----
        key_is_down = any_key_down()#检查是否有按键被按下
        if key_is_down and not key_was_down:
            time = 12
        key_was_down = key_is_down

        if time>0:
            time-=1

        #----渲染----
        screen.fill((240,240,240))
        x = screen.get_width() // 2 - begin.get_width() // 2
        y = screen.get_height() // 2 - begin.get_height() // 2
        #获取图片需要放置的坐标

        if time > 9:
            screen.blit(middle, (x, y))
        elif time > 4:
            screen.blit(end, (x, y))
        elif time > 0:
            screen.blit(middle, (x, y))
        else:
            screen.blit(begin, (x, y))

                # ============================================================
                # ⑤ 翻到屏幕前 + 限制帧率
                # ============================================================
        pygame.display.flip()
        clock.tick(80)


if __name__ == "__main__":
    main() 