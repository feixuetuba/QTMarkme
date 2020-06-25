import cv2
from PyQt5.QtGui import QImage

def cv_load_as_qim(path, mode="RGB"):
    image = cv2.imread(path)
    if image is None:
        return None
    h, w = image.shape[:2]
    if mode == "RGB":
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        qimage = QImage(image,w, h, QImage.Format_RGB888)
    elif mode == "RGBA":
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
        qimage = QImage(image, w, h, QImage.Format_ARGB32)
    return qimage