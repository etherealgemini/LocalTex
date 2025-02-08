import PIL
import cv2
import numpy as np
from PyQt6.QtGui import QImage
from PIL import Image


def qimage_to_pil(qimage: QImage) -> PIL.Image.Image:
    """将 QImage 转换为 PIL 图像"""
    # 确保是 RGB 格式
    qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
    width = qimage.width()
    height = qimage.height()

    # 获取 QImage 数据指针
    ptr = qimage.bits()
    ptr.setsize(qimage.sizeInBytes())

    # 将数据指针转换为 numpy 数组并转换为 PIL 图像
    arr = np.array(ptr).reshape((height, width, 3))  # 每个像素3个字节(RGB)
    pil_image = Image.fromarray(arr)  # 转换为 PIL 图像
    return pil_image


def pil_to_qimage(pilimage: PIL.Image.Image) -> QImage:
    pil_image = pilimage.convert("RGB")  # 确保是RGB模式
    data = pil_image.tobytes("raw", "RGB")
    q_image = QImage(data, pil_image.width, pil_image.height, pil_image.width * 3, QImage.Format.Format_RGB888)
    return q_image


class CropByProject:
    """
    投影法裁剪
    reference: https://www.cnblogs.com/shiwanghualuo/p/17794765.html
    """

    def __init__(self, threshold: int = 250):
        self.threshold = threshold

    def __call__(self, origin_img) -> np.ndarray:
        image = cv2.cvtColor(origin_img, cv2.COLOR_BGR2GRAY)

        # 反色，将大于threshold的值置为0，小于的改为255
        retval, img = cv2.threshold(image, self.threshold, 255, cv2.THRESH_BINARY_INV)

        # 使文字增长成块
        closed = cv2.dilate(img, None, iterations=1)

        # 水平投影
        x0, x1 = self.get_project_loc(closed, direction="width")

        # 竖直投影
        y0, y1 = self.get_project_loc(closed, direction="height")

        return origin_img[y0:y1, x0:x1]

    @staticmethod
    def get_project_loc(img, direction):
        """获得裁剪的起始和终点索引位置
        Args:
            img (ndarray): 二值化后得到的图像
            direction (str): 'width/height'
        Raises:
            ValueError: 不支持的求和方向
        Returns:
            tuple: 起始索引位置
        """
        if direction == "width":
            axis = 0
        elif direction == "height":
            axis = 1
        else:
            raise ValueError(f"direction {direction} is not supported!")

        loc_sum = np.sum(img == 255, axis=axis)
        loc_range = np.argwhere(loc_sum > 0)
        i0, i1 = loc_range[0][0], loc_range[-1][0]
        return i0, i1
