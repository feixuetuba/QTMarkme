import os
import sys

import yaml
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QListWidget, QListWidgetItem

from utils.LabelMaker import LMDrawLabel

from utils.QtFilUtils import choose_dir
from utils.UiUtils import get_cursor


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.supported = ["jpg", "jpeg", "png", "bmp"]
        self.src_dir = None
        self.dest_dir = None
        self.initUI()
        self.cwd = os.getcwd()
        self.current_item = None

    def initUI(self):
        self.resize(1366, 768)
        self.setWindowTitle('LabelScratch')
        self.lb = LMDrawLabel(self)
        self.lb.setGeometry(QRect(20, 30, 1024, 700))
        self.lb.show_image('images/lena.png')
        self.__init_menu()
        #self.lb.setCursor()

        self.img_list_widget = QListWidget(self)
        self.img_list_widget.itemClicked.connect(self.slot_open_img_item)
        # 设置样式，直接在函数中设置
        self.img_list_widget.setStyleSheet("QListWidget{border:1px solid gray; color:black; }"
                                   "QListWidget::Item{padding-top:1px; padding-bottom:1px; }"
                                   "QListWidget::Item:hover{background:skyblue; }"
                                   "QListWidget::item:selected{background:lightgray; color:red; }"
                                   "QListWidget::item:selected:!active{border-width:0px; background:lightgreen; }"
                                   )
        self.img_list_widget.setGeometry(1050,20, 316, 700)
        self.__load_config("./cfg.yaml")
        self.lb.setCursor(get_cursor(5))
        self.statusBar().showMessage(f"已就绪...")
        self.show()

    def im_check(self, fname):
        if self.dest_dir is None:
            return False
        d = os.path.join(self.dest_dir, fname)
        if not os.path.isfile(d):
            return False
        return True

    def load_img_list(self, img_fnames):
        if self.src_dir is None:
            self.statusBar().showMessage("未指定图片源目录")
            return
        self.img_list_widget.clear()
        for fname in img_fnames:
            labeled = self.im_check(fname)
            if labeled:
                item = QListWidgetItem(f"{fname} *")
            else:
                item = QListWidgetItem(f"{fname}")
            self.img_list_widget.addItem(item)

    def __load_config(self, cfg_file="./cfg.yaml"):
        if not os.path.isfile(cfg_file):
            return
        with open(cfg_file) as fd:
            try:
                cfg = yaml.load(fd, Loader=yaml.FullLoader)
            except:
                cfg = yaml.load(fd)
        if "dest" in cfg:
            if os.path.isdir(cfg["dest"]):
                self.dest_dir = cfg["dest"]

        if "src" in cfg:
            if os.path.isdir(cfg["src"]):
                self.load_dir(cfg["src"])

    def __init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&文件')
        edit_menu = menubar.addMenu('&编辑')

        menus = [
            ("Open file", "Ctrl+o"),
            ("Open dir", None),
            ("Save as", "Ctrl+s"),
            ("Crop begin", "Ctrl+x"),
            ("Crop confirm", "Ctrl+c"),
            ("Crop cancel", "Esc")
        ]

        for menu, shortcut in menus:
            action = QAction(menu, file_menu)
            if shortcut is not None:
                action.setShortcut(shortcut)
            slot = menu.lower().replace(" ", "_")
            slot = f"slot_{slot}"
            action.triggered.connect(getattr(self, slot))
            file_menu.addAction(action)
            self.dest_dir = None

        menus = [
            ("Thick more", "Ctrl+Shift+="),
            ("Slim more", "Ctrl+-"),
        ]

        for menu, shortcut in menus:
            action = QAction(menu, edit_menu)
            if shortcut is not None:
                action.setShortcut(shortcut)
            slot = menu.lower().replace(" ", "_")
            slot = f"slot_{slot}"
            action.triggered.connect(getattr(self, slot))
            edit_menu.addAction(action)
            self.dest_dir = None

    def slot_open_dir(self):
        dir_choosed = choose_dir(self)
        if dir_choosed == "":
            return
        self.load_dir(dir_choosed)

    def load_dir(self, dir_choosed):
        self.statusBar().showMessage("目录加载中")
        images = []
        for f in os.listdir(dir_choosed):
            surf = f.split(".")[-1]
            if surf not in self.supported:
                continue
            full_f = os.path.join(dir_choosed, f)
            if not os.path.isfile(full_f):
                continue
            images.append(f)

        self.src_dir = dir_choosed
        self.load_img_list(images)
        self.statusBar().showMessage("加载完成")

    def slot_open_img_item(self, item):
        file_choosed = os.path.join(self.src_dir, item.text())
        self.statusBar().showMessage(f"打开文件{file_choosed}")
        self.current_item = item
        self.lb.show_image(file_choosed)

    def slot_open_file(self):
        file_choosed, file_type = QFileDialog.getOpenFileName(self,
                                                            "选取文件",
                                                            self.cwd,  # 起始路径
                                                            "jpeg (*.jpg *.jpeg);;png (*.png);;bmp (*.bmp)")  # 设置文件扩展名过滤,用双分号间隔

        if file_choosed == "":
            self.statusBar().showMessage("取消选择")
            return None
        self.statusBar().showMessage(f"打开文件{file_choosed}")
        self.lb.show_image(file_choosed)

    def slot_open_files(self):
        files, filetype = QFileDialog.getOpenFileNames(self,
                                                       "多文件选择",
                                                       self.cwd,  # 起始路径
                                                       "jpeg (*.jpg *.jpeg);;png (*.png);;bmp (*.bmp)")

        if len(files) == 0:
            self.statusBar().showMessage("取消选择")
            return
        self.files = files

    def slot_save_as(self):
        if (self.current_item is not None) or (self.dest_dir is None) or (not os.path.isdir(self.dest_dir)):
            file_choosed, filetype = QFileDialog.getSaveFileName(self,
                                                                    "文件保存",
                                                                    self.cwd,  # 起始路径
                                                                    "jpeg (*.jpg *.jpeg);;png (*.png);;bmp (*.bmp)")
        else:
            file_choosed = os.path.join(self.dest_dir, self.current_item.text())
        if file_choosed == "":
            self.statusBar().showMessage("未保存")
            return []
        self.lb.save_result(file_choosed)
        self.statusBar().showMessage(f"文件{file_choosed}保存成功")
        if self.current_item is not None:
            txt = self.current_item.text()
            if "*" not in txt:
                self.current_item.setText(f"{txt} *")

    def slot_crop_begin(self):
        self.statusBar().showMessage(f"剪裁模式")
        self.lb.start_crop()

    def slot_crop_confirm(self):
        self.statusBar().showMessage(f"剪裁中...")
        self.lb.do_crop()
        self.statusBar().showMessage(f"已就绪...")

    def slot_crop_cancel(self):
        self.lb.cancel_crop()

    def slot_thick_more(self):
        pen = self.lb.getPen()
        w = pen.width() + 1
        pen.setWidth(w)
        cursor = get_cursor(w)
        self.lb.setCursor(cursor)
        self.lb.setPen(pen)

    def slot_slim_more(self):
        pen = self.lb.getPen()
        w = max(0, pen.width() -1)
        pen.setWidth(w)
        cursor = get_cursor(w)
        self.lb.setCursor(cursor)
        self.lb.setPen(pen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())