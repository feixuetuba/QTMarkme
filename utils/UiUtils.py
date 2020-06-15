from PyQt5.QtCore import Qt, QPoint, QRectF
from PyQt5.QtGui import QImage, QPixmap, QPainter, QCursor


def get_cursor(width):
    pix = QPixmap("resources/cursor.png")
    pix = pix.scaled(width,width)
    return QCursor(pix)