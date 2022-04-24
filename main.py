import sys
import os
import numpy as np
import cv2 as cv
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from dataMarker import *
from pathlib import Path

LABELING = 1  # 标注状态
PREVIEW = 0  # 预览状态


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setFont(QFont('SansSerif', 15))

        print(f'opencv 版本为：{cv.__version__}')
        
        # centerFrame
        self.imagesFold, self.labelsFold = None, None
        self.image, qImg = None, None
        self.imagesPaths = list()
        self.suffixs = ['jpg', 'png']
        self.selectImagesFolder.clicked.connect(self.getImagesFold)
        self.selectLabelsFolder.clicked.connect(self.getLabelsFold)
        self.imagesFolderName.editingFinished.connect(self.loadImages)  # 失去焦点或回车
        self.labelsFolderName.editingFinished.connect(self.labelSelected)
        self.model = PREVIEW

        # rightFrame
        self.rightFrame.setFont(QFont('SansSerif', 12))
        self.imageLists.itemClicked.connect(self.clickItem)

    @pyqtSlot(bool)
    def getImagesFold(self):
        dlg = QFileDialog(self, '选择数据文件夹', 'E:\\')
        dlg.setFileMode(QFileDialog.Directory)
        foldName = dlg.getExistingDirectory()  # 打开文件夹
        # print(f'foldName=={foldName}')
        if foldName != '':  # 不为空，就是退出没选的情况
            self.imagesFold = Path(foldName)
            self.labelsFold = self.imagesFold.parent / 'labels'

            self.imagesFolderName.setText(str(self.imagesFold))
            self.labelsFolderName.setText(str(self.labelsFold))
            self.loadImages()
            if self.imageLists.item(0):
                self.selectImage(self.imageLists.item(0))

    @pyqtSlot(bool)
    def getLabelsFold(self):
        dlg = QFileDialog(self, '选择标签存放文件夹', 'E:\\')
        dlg.setFileMode(QFileDialog.Directory)
        foldName = dlg.getExistingDirectory()  # 打开文件夹
        if foldName != '':  # 不为空，就是退出没选的情况
            self.labelsFold = Path(foldName)
            self.labelsFolderName.setText(str(self.labelsFold))
            self.labelSelected()

    def labelSelected(self):
        print(f'标签存放文件夹: {self.labelsFolderName.text()}')

    def loadImages(self):
        try:
            if self.imagesFolderName.text() != '':
                self.imageLists.clear()
                self.imagesPaths.clear()
                print(f'数据文件夹: {self.imagesFolderName.text()}')
                print("检测到图片: ")
                for suffix in self.suffixs:
                    for path in self.imagesFold.glob(f'*.{suffix}'):
                        self.imagesPaths.append(path)

                self.imagesPaths.sort()
                for path in self.imagesPaths:
                    self.imageLists.addItem(str(path))
                    print(path)

                print("图片END")
            else:
                print("数据文件夹为空")
        except OSError:
            print(f'OSError, 文件夹不存在')

    def clickItem(self, item):
        self.selectImage(item)

    def selectImage(self, item):
        """
        显示图片，为了美观，对图片进行缩放，固定图片的最长边多大。缩放拖动再说。
        :param item:
        :return:
        """
        try:
            path = item.text()
            print(f'selected image_path = {path}')

            # self.image = QImage(path)
            self.image = cv.imread(path, 1)
            if self.image is None:
                print(f'图片读取失败，路径为:{path}')
            width, height = self.imageFrame.width(), self.imageFrame.height()
            imgWidth, imgHeight = self.image.shape[1], self.image.shape[0]
            # print(self.image.shape)
            scale = min(width * 0.8 / imgWidth, height * 0.8 / imgHeight)
            imgWidth, imgHeight = round(imgWidth * scale), round(imgHeight * scale)

            # if imgWidth > imgHeight:
            #     scale = width*0.8 / imgWidth
            #     imgWidth, imgHeight = round(imgWidth*scale), round(imgHeight*scale)
            #
            # else:
            #     scale = height * 0.8 / imgHeight
            #     imgWidth, imgHeight = round(imgWidth * scale), round(imgHeight * scale)

            self.image = cv.resize(self.image, (imgWidth, imgHeight))  # (w, h), shape--(h,w,c)
            bytesPerLine = 3 * imgWidth
            self.qImg = QImage(self.image.data, imgWidth, imgHeight, bytesPerLine,
                               QImage.Format_RGB888).rgbSwapped()

            self.showImage.setPixmap(QPixmap.fromImage(self.qImg))
            """大的w, h、 图片x, y
            图片的center = 大的的center
            (w/2, h/2)
            图片的左上点(w/2 - x/2, h/2 - y/2)
            """
            self.showImage.setGeometry(round(width / 2 - imgWidth / 2), round(height / 2 - imgHeight / 2),
                                       imgWidth, imgHeight)  # x,y,w,h

            self.imageLists.setCurrentItem(item)
        except :
            print("加载图片出错, 可能是含有中文之类")


def link_image():
    print('点击了图片')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.setFixedSize(1280, 720)

    myWin.show()
    sys.exit(app.exec_())
