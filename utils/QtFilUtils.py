from PyQt5.QtWidgets import QFileDialog
import os

def choose_dir(parent):
    dir_choose = QFileDialog.getExistingDirectory(parent,
                                                  "选取文件夹",
                                                  os.getcwd())  # 起始路径
    return dir_choose
    

def choose_file(parent):
    fileName_choose, filetype = QFileDialog.getOpenFileName(parent,
                                                            "选取文件",
                                                            os.getcwd(),  # 起始路径
                                                            "jpeg (*.jpg *.jpeg);;png (*.png);;bmp (*.bmp)")  # 设置文件扩展名过滤,用双分号间隔

    return fileName_choose 


def choose_muti_file(parent):
    files, filetype = QFileDialog.getOpenFileNames(parent,
                                                   "多文件选择",
                                                   parent.cwd,  # 起始路径
                                                   "jpeg (*.jpg *.jpeg);;png (*.png);;bmp (*.bmp)")

    if len(files) == 0:
        parent.statusBar().showMessage("取消选择")
        return []
    return files


def choose_save_file(parent):
    fileName_choose, filetype = QFileDialog.getSaveFileName(parent,
                                                            "文件保存",
                                                            parent.cwd,  # 起始路径
                                                            "jpeg (*.jpg *.jpeg);;png (*.png);;bmp (*.bmp)")

    return fileName_choose, filetype