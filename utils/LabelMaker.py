import cv2
import numpy as np
from PyQt5.QtCore import Qt, QPoint, QRectF
from PyQt5.QtGui import QPainter, QImage, QPixmap, QPen, QColor
from PyQt5.QtWidgets import QLabel


class CVImageWrapper:
    def __init__(self):
        self.m_w = 512
        self.m_h = 512
        self.scale_ratio = 1.0
        self.mask = None
        self.thickness = 3
        self.im_w = 0
        self.im_h = 0
        self.latest_x = 0
        self.latest_y = 0

    def set_shape(self, h:float, w:float):
        self.m_w = float(w)
        self.m_h = float(h)

    def load_image(self, src):
        image = cv2.imread(src)
        if image is None:
            return None
        h, w= image.shape[:2]
        self.im_w = w
        self.im_h = h
        self.mask = np.zeros((h,w), dtype=np.uint8)
        ratio = max(h/self.m_h, w/self.m_w)
        h = h / ratio
        w = w / ratio
        image = cv2.resize(image, (int(w),int(h)))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.scale_ratio = ratio
        return image

    def save(self, dest):
        cv2.imwrite(dest, self.mask)

class QTImageWrapper:
    def __init__(self):
        self.im_size = None
        self.win_h = 0
        self.win_w = 0
        self.ori_img = None
        self.result = None
        self.ratio = 1.0

    def set_shape(self, h:float, w:float):
        self.win_w = float(w)
        self.win_h = float(h)

    def load_image(self, src):
        type_src = type(src)
        if type_src is str:
            self.ori_img = QImage(src)
        elif type_src is QImage:
            self.ori_img = src
        if self.ori_img is None:
            return None
        self.im_size = self.ori_img.size()
        h, w= self.im_size.height(), self.im_size.width()
        ratio = max(h/self.win_h, w/self.win_w)
        h = h / ratio
        w = w / ratio
        self.ratio = ratio
        return self.ori_img.scaled(w,h)

    def crop(self, rect):
        x = rect.x() * self.ratio
        y = rect.y() * self.ratio
        w = rect.width() * self.ratio
        h = rect.height() * self.ratio
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)
        image = self.ori_img.copy(x,y,w,h)
        return self.load_image(image)


    def save_result(self, mask, dest):
        h = self.im_size.height()
        w = self.im_size.width()
        self.result = QImage(2*w, h, QImage.Format_RGB32)       # 这个result一定要设置为class的内部成员，不然程序可能会在这步之后异常退出
        mask = mask.convertToFormat(QImage.Format_RGB32)
        mask = mask.scaled(w,h)
        painter = QPainter(self.result)
        painter.drawImage(0, 0, self.ori_img)
        painter.drawImage(w, 0, mask)
        self.result.save(dest)

class LMDrawLabel(QLabel):
    DRAW = 0
    ERASE = 1
    def __init__(self, *args, **kwargs):
        super(LMDrawLabel, self).__init__(*args, **kwargs)
        self.im_wrap = QTImageWrapper()
        self.bg = QPixmap()
        self.min_x = 0
        self.min_y = 0
        self.max_x = -1
        self.max_y = -1
        self.pix = QPixmap()  # 实例化一个 QPixmap 对象
        self.lastPoint = None  # 起始点
        self.endPoint = None  # 终点
        self.__pen = QPen(QColor(255,0,0,50), 5, Qt.SolidLine)
        self.crop_mode = False
        
    def show_image(self, src):
        self.im_wrap.set_shape(self.width(), self.height())
        image = self.im_wrap.load_image(src)
        self.__show_image(image)
        self.update()

    def __show_image(self, image):
        self.bg = QPixmap.fromImage(image)
        self.pix = QPixmap(image.width(), image.height())
        self.pix.fill(Qt.transparent)
        self.painter_status = self.ERASE
        self.max_x = self.min_x + image.width()
        self.max_y = self.min_y + image.height()

    def setGeometry(self, *args, **kwargs) -> None:
        super().setGeometry(*args, **kwargs)

    def setPen(self, pen:QPen):
        self.__pen = pen

    def getPen(self):
        return self.__pen

    # 重绘的复写函数 主要在这里绘制
    def paintEvent(self, event):
        pp = QPainter(self.pix)
        # 根据鼠标指针前后两个位置绘制直线
        pp.setPen(self.__pen)

        if self.crop_mode:
            pp = QPainter(self)
            pp.setPen(QPen(Qt.red, 4, Qt.SolidLine))
            pp.drawPixmap(0, 0, self.bg)
            if self.lastPoint is not None:
                pp.drawRect(QRectF(self.lastPoint, self.endPoint))
        else:
            if self.painter_status == self.ERASE:
                pen = QPen()
                pen.setWidth(10)
                pp.setCompositionMode(QPainter.CompositionMode_Clear)
                pp.setPen(pen)
            if self.lastPoint is not None:
                pp.drawLine(self.lastPoint, self.endPoint)
            # 让前一个坐标值等于后一个坐标值，
            # 这样就能实现画出连续的线
            self.lastPoint = self.endPoint
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.bg)
            painter.drawPixmap(0, 0, self.pix)  # 在画布上画出

    def __clip_point(self, point):
        x = max(self.min_x, point.x())
        y = max(self.min_x, point.y())

        x = min(self.max_x, x)
        y = min(self.max_y, y)

        return QPoint(x, y)

    # 鼠标按压事件
    def mousePressEvent(self, event):
        # 鼠标左键按下
        btn = event.button()
        if btn == Qt.LeftButton:
            self.lastPoint = self.__clip_point(event.pos())
            self.endPoint = self.lastPoint
            self.painter_status = self.DRAW
        elif btn == Qt.RightButton:
            self.lastPoint = self.__clip_point(event.pos())
            self.endPoint = self.lastPoint
            self.painter_status = self.ERASE

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        # 鼠标左键按下的同时移动鼠标
        if event.buttons() and Qt.LeftButton:
            self.endPoint = self.__clip_point(event.pos())

            # 进行重新绘制
            self.update()

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        # 鼠标左键释放
        if event.button() == Qt.LeftButton:
            self.endPoint = self.__clip_point(event.pos())
            # 进行重新绘制
            self.update()

    def save_result(self, dest):
        self.im_wrap.save_result(self.pix.toImage(), dest)

    def start_crop(self):
        self.crop_mode = True

    def cancel_crop(self):
        if not self.crop_mode:
            return
        if self.lastPoint is None:
            return
        self.lastPoint = None
        self.update()
        self.crop_mode = False

    def do_crop(self):
        if not self.crop_mode:
            return
        if self.lastPoint is None:
            return
        rect = QRectF(self.lastPoint, self.endPoint)
        if rect.width() > 0 and rect.height() > 0:
            image = self.im_wrap.crop(rect)
            self.__show_image(image)
        self.cancel_crop()