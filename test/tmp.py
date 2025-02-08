import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QScrollArea, QLabel, QVBoxLayout, QWidget, QSlider, QHBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("图片查看器")
        self.setGeometry(100, 100, 800, 600)

        # 创建滚动区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)  # 自动调整滚动区域的大小
        self.setCentralWidget(self.scroll_area)

        # 创建 QLabel 用于显示图片
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setPixmap(QPixmap())  # 初始为空
        self.scroll_area.setWidget(self.image_label)

        # 创建滑动条用于调整图片大小
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(10)  # 最小缩放比例
        self.slider.setMaximum(200)  # 最大缩放比例
        self.slider.setValue(100)  # 默认值
        self.slider.valueChanged.connect(self.update_image_scale)

        # 创建按钮用于加载图片
        self.load_button = QPushButton("加载图片")
        self.load_button.clicked.connect(self.load_image)

        # 布局
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.load_button)
        control_layout.addWidget(self.slider)

        main_layout = QVBoxLayout()
        main_layout.addLayout(control_layout)

        container_widget = QWidget()
        container_widget.setLayout(main_layout)
        self.scroll_area.setWidget(container_widget)

    def load_image(self):
        """加载图片"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.bmp *.gif)")
        if file_path:
            self.image_label.setPixmap(QPixmap(file_path))
            self.update_image_scale(self.slider.value())

    def update_image_scale(self, value):
        """根据滑动条的值更新图片大小"""
        pixmap = self.image_label.pixmap()
        if pixmap:
            scaled_pixmap = pixmap.scaled(
                pixmap.width() * value // 100,
                pixmap.height() * value // 100,
                Qt.AspectRatioMode.KeepAspectRatio
            )
            self.image_label.setPixmap(scaled_pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec())