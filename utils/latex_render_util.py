import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QImage, QPainter, QWheelEvent
from PyQt6.QtWidgets import QWidget, QScrollArea
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from utils.image_util import CropByProject

plt.style.use('fivethirtyeight')
mpl.rcParams['text.usetex'] = True


class LaTeXViewer(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__()

        self.parent_ = parent
        self.latex_code = None
        self.q_image = None
        self.scale_factor = 1.0
        self.setWindowTitle("LaTeX Viewer with Zoom")
        # self.setGeometry(100, 100, 800, 600)
        self.font_size = 12
        latex_code = r"example: $x ^ 2 - 2 x + 1 = 0$"
        self.q_width = 300
        self.cropper = CropByProject()

        # 设置拉伸比例和渲染的Latex字符串
        self.render_latex(latex_code)

        # self.setLayout(self.layout)

    def render_latex(self, latex_code):
        # print('render')
        self.latex_code = latex_code

        fig = plt.figure(linewidth=1, facecolor="white", layout="tight", dpi=300)
        fig.text(0, 0.5, latex_code)
        canvas = FigureCanvas(fig)
        canvas.draw()
        # width, height = fig.canvas.get_width_height()
        cropper = CropByProject()
        image_data = canvas.buffer_rgba()
        width, height = canvas.get_width_height()
        rgba_array = np.frombuffer(image_data, dtype=np.uint8).reshape(height, width, 4)
        cropped = cropper(rgba_array)

        height, width, channels = cropped.shape

        # 将图像转换为QImage
        q_image = QImage(cropped.tobytes(), width, height, QImage.Format.Format_RGBA8888)
        self.q_width *= self.scale_factor
        self.q_image = q_image.scaledToWidth(self.q_width)
        plt.close(fig)
        return

    def paintEvent(self, event):
        if not self.q_image:
            return
        self.render_latex(self.latex_code)

        img_width = self.q_image.width()
        img_height = self.q_image.height()
        painter = QPainter(self)
        painter.save()
        # 计算绘制区域的中心位置
        x = (self.width() - img_width) // 2
        y = (self.height() - img_height) // 2

        rect = QRect(x, y, img_width, img_height)
        painter.drawImage(rect, self.q_image)
        painter.restore()
        self.scale_factor = 1

    def wheelEvent(self, event: QWheelEvent):
        # 根据滚轮事件进行缩放
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.scale_factor = factor
        self.update()
        self.adjust_size()

    def adjust_size(self):
        if self.q_image:
            new_width = self.q_image.width()
            new_height = self.q_image.height()
            self.setFixedSize(new_width*1.1,new_height*1.1)
