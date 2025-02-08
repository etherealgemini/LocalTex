import tkinter as tk
from PIL import ImageGrab
import os


class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("用户自定义框选截图")

        # 创建一个透明窗口
        self.root.attributes("-alpha", 0.1)  # 设置透明度
        self.root.attributes("-fullscreen", True)  # 全屏显示
        self.root.configure(cursor="crosshair")  # 设置鼠标指针为十字形状

        # 创建一个Canvas覆盖整个窗口
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 初始化变量
        self.start_x = None
        self.start_y = None
        self.rect = None

        # 绑定鼠标事件
        self.root.bind("<ButtonPress-1>", self.on_press)
        self.root.bind("<B1-Motion>", self.on_move)
        self.root.bind("<ButtonRelease-1>", self.on_release)
        self.captured = None

    def on_press(self, event):
        # 鼠标按下时记录起始点
        self.start_x = event.x
        self.start_y = event.y

    def on_move(self, event):
        # 鼠标移动时绘制矩形
        if self.rect:
            self.canvas.delete(self.rect)  # 删除之前的矩形
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline="red", width=2
        )

    def on_release(self, event):
        # 鼠标释放时截图
        if self.rect:
            self.canvas.delete(self.rect)  # 删除矩形
        self.root.destroy()  # 关闭窗口

        # 获取截图区域
        x1, y1, x2, y2 = self.start_x, self.start_y, event.x, event.y
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        # 使用Pillow进行截图
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        self.captured = screenshot


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()