# 自嘲熊桌宠 🐻

一只会跟着你打字的自嘲熊桌宠——灵感来自 Bongo Cat Mver。

## 功能

- ⌨️ **打字动画**：你敲键盘，熊跟着打拍子
- 🐭 **拖拽移动**：左键按住熊拖动到任意位置
- 🔍 **右键缩放**：右键按住熊左右拖动调整大小
- 📌 **窗口置顶**：始终在最上层
- 🫥 **透明背景**：熊悬浮在桌面上
- 🔔 **系统托盘**：最小化到托盘，右键菜单控制

## 运行

### 方式一：Python 源码

```bash
pip install pygame pystray pillow
python main.py
```

### 方式二：EXE（无需 Python）

下载 `dist/main.exe`，双击运行。

## 操作

| 操作 | 方式 |
|------|------|
| 移动熊 | 左键按住熊拖动 |
| 缩放熊 | 右键按住熊左右拖动 |
| 隐藏/显示 | 右下角托盘右键菜单 |
| 退出 | 托盘菜单 "退出" |

## 技术栈

- Python 3
- Pygame（渲染 + 键盘检测）
- ctypes（Windows API：透明窗口、全局按键、置顶）
- pystray（系统托盘）
- PyInstaller（打包 EXE）

## 致谢

启发自 [Bongo Cat Mver](https://github.com/kuroni/bongocat-osu) —— 一个配合 osu! 使用的桌面猫。
