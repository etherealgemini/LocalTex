import sys
import tkinter as tk
from typing import Union

import typing
from PIL.Image import Image
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, \
    QWidget, QScrollArea, QSizePolicy

from utils.image_util import pil_to_qimage, qimage_to_pil
from utils.latex_render_util import LaTeXViewer
from utils.screenshot_util import ScreenshotApp


class Image2LatexApp(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化界面
        self.image:Image = None
        self.setWindowTitle("Image2Latex")
        self.setGeometry(100, 100, 1000, 600)  # 设置窗口更宽以容纳两个区域

        # 创建布局
        self.layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.bottom_layout = QVBoxLayout()

        # 创建按钮区域
        # 上传图片按钮
        self.upload_button = self.create_button('upload', self.upload_image)
        # 截图按钮
        self.screenshot_button = self.create_button('screenshot', self.take_screenshot)
        # 启动按钮
        self.start_button = self.create_button('launch', self.start_processing)

        self.button_layout.addWidget(self.upload_button)
        self.button_layout.addWidget(self.screenshot_button)
        self.button_layout.addWidget(self.start_button)

        # 图片显示区域（左侧）
        self.image_display = QLabel(self)
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setText("no figure yet")
        self.image_display.setMinimumSize(300, 300)

        # LaTeX 渲染区域（右侧）
        self.latex_render_scroll_area = QScrollArea()
        self.latex_renderer = LaTeXViewer(self.latex_render_scroll_area)
        self.latex_renderer.setMinimumSize(0,0)
        self.latex_render_scroll_area.setWidget(self.latex_renderer)
        self.latex_render_scroll_area.setWidgetResizable(True)
        self.latex_render_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.latex_render_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.latex_render_scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.latex_render_scroll_area.setMaximumWidth(self.width()//2)

        # LaTeX 文本显示区域
        self.latex_text_area = QTextEdit(self)
        self.latex_text_area.setMaximumHeight(400)
        self.latex_text_area.setFontPointSize(16)
        self.latex_text_area.setPlaceholderText('generate something...')

        # 添加组件到总布局
        self.middle_layout.addWidget(self.image_display)
        self.middle_layout.addWidget(self.latex_render_scroll_area)
        self.bottom_layout.addWidget(self.latex_text_area)

        self.layout.addLayout(self.middle_layout)
        self.layout.addLayout(self.button_layout)
        self.layout.addLayout(self.bottom_layout)

        self.model = None

    @staticmethod
    def create_button(text, slot):
        """创建带有现代风格的按钮"""
        button = QPushButton(text)
        button.clicked.connect(slot)

        # 设置按钮样式
        button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3; /* 按钮背景色 */
                color: white;              /* 字体颜色 */
                border: none;              /* 边框去除 */
                padding: 10px 20px;        /* 内边距 */
                font-size: 20px;           /* 字体大小 */
                border-radius: 8px;        /* 圆角 */
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4dabf5; /* 悬停时的背景色 */
            }
            QPushButton:pressed {
                background-color: #1769aa; /* 按下时的背景色 */
            }
        """)
        return button

    def upload_image(self):
        # 文件选择对话框
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Image Files (*.png *.jpg *.bmp *.jpeg)")
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            image_path = file_paths[0]
            # 显示上传的图片
            self.display_image(image_path)
            print(f"Uploaded image: {image_path}")

    def display_image(self, image_: Union[str, Image]):
        # 使用 QPixmap 显示图片
        if isinstance(image_, str):
            pixmap = QPixmap(image_)
            self.image = qimage_to_pil(pixmap.toImage())
        elif isinstance(image_, Image):
            q_image = pil_to_qimage(image_)
            pixmap = QPixmap.fromImage(q_image)
            self.image = image_
        else:
            self.image_display.setText("图片加载失败")
            return

        if not pixmap.isNull():
            self.image_display.setPixmap(
                pixmap.scaled(self.image_display.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.image_display.setText("图片加载失败")

    def take_screenshot(self):
        root = tk.Tk()
        app = ScreenshotApp(root)
        root.mainloop()
        if app.captured is not None:
            self.display_image(app.captured)

    def start_processing(self):
        if self.image is None:
            return

        if self.model is None:
            from model.Qwen2VLOCR import Qwen2VLOCR
            self.model = Qwen2VLOCR()
            self.model.load()

        generated_latex = self.model.process(self.image)
        if '$' not in generated_latex:
            generated_latex = '$' + generated_latex + '$'
        # generated_latex = r"\[ x = {-b \pm \sqrt{b^2-4ac} \over 2a} \]"

        self.latex_text_area.setText(generated_latex)
        self.latex_renderer.render_latex(generated_latex)
        self.latex_renderer.update()

    def resizeEvent(self, a0: typing.Optional[QtGui.QResizeEvent]) -> None:
        super().resizeEvent(a0)
        self.latex_render_scroll_area.setMaximumWidth(self.width() // 2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Image2LatexApp()
    window.show()
    sys.exit(app.exec())
