import os
import cv2
from PyQt6.QtCore import Qt, QRect, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPixmap, QImage, QColor
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QMessageBox, QLabel
from src.utils.translator import TencentTranslator

class PreviewWindow(QWidget):
    def __init__(self, parent, image_path, ocr_result):
        super().__init__(parent, Qt.WindowType.Window)
        self.parent = parent
        self.image_path = image_path
        self.ocr_result = ocr_result
        self.translated_text = []  # 存储翻译后的文本
        self.initUI()
        self.setupTimer()  # 设置定时器

    def initUI(self):
        # 读取图片并获取尺寸
        image = cv2.imread(self.image_path)
        image_height, image_width = image.shape[:2]

        # 获取屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # 设置最大窗口大小为屏幕大小
        max_width = screen_width
        max_height = screen_height

        # 设置窗口大小为图片大小，但不超过最大窗口大小
        width = min(image_width, max_width)
        height = min(image_height, max_height)

        # 设置窗口大小和位置
        self.setGeometry(0, 0, width, height)

        # 计算窗口居中位置
        self.move(int((screen_width - width) / 2), int((screen_height - height) / 2))

        # 转换图片为QPixmap
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image_rgb.shape
        bytes_per_line = ch * w
        image_qt = QImage(image_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.pixmap = QPixmap.fromImage(image_qt)

        self.setWindowTitle('OCR预览')
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)

        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

    def setupTimer(self):
        # 创建一个定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.closeWindow)  # 定时器超时时调用关闭窗口的函数
        self.timer.start(3000)  # 设置定时器间隔为3000毫秒（3秒）

    def closeWindow(self):
        # 关闭窗口
        self.close()
        # 删除截图文件
        if os.path.exists(self.image_path):
            os.remove(self.image_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 启用抗锯齿
        painter.drawPixmap(0, 0, self.pixmap)

        # 设置字体
        font = QFont('Microsoft YaHei', 11)  # 使用微软雅黑字体
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)

        texts = self.ocr_result.text

        for box, text in zip(self.ocr_result.boxes, texts):
            x, y = int(box[0]), int(box[1])

            # 计算文本区域
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            padding = 4
            vertical_offset = 2  # 向下偏移量

            # 绘制半透明背景
            bg_rect = QRect(x - padding, y - text_height + vertical_offset,
                          text_width + padding * 2, text_height + padding * 2)
            bg_color = QColor(0, 0, 0, 160)  # 黑色背景，透明度为160
            painter.fillRect(bg_rect, bg_color)

            # 绘制文本边框
            border_color = QColor(46, 204, 113, 200)  # 绿色边框
            painter.setPen(border_color)
            painter.drawRect(bg_rect)

            # 绘制文本
            text_color = QColor(255, 255, 255)  # 白色文本
            painter.setPen(text_color)
            painter.drawText(x, y + vertical_offset * 2, text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()