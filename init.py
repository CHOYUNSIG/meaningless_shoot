import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication
from game import Game


class Init(QWidget):
    def __init__(self):
        super().__init__()
        self.game_start = False
        self.fps = 60
        self.size = (800, 600)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('meaningless: settings')
        self.resize(300, 150)
        sqr = self.frameGeometry()
        sqr.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(sqr.topLeft())

        btn_start = QPushButton('&Start', self)
        btn_start.clicked.connect(self.start)

        select_fps = QComboBox(self)
        for i in range(30, 301, 10):
            select_fps.addItem('%d' % i)
        select_fps.setCurrentText('60')
        select_fps.activated[str].connect(self.setting_fps)
        box_fps = QVBoxLayout()
        box_fps.addStretch(6)
        box_fps.addWidget(QLabel('FPS', self), 1)
        box_fps.addWidget(select_fps, 1)
        box_fps.addStretch(3)

        select_size = QComboBox(self)
        for size in [
            '640x480 (4:3)',
            '960x720 (4:3)',
            '1200x900 (4:3)',
            '853x480 (16:9)',
            '1280x720 (16:9)',
            '1600x900 (16:9)',
            '768x480 (16:10)',
            '1152x720 (16:10)',
            '1440x900 (16:10)'
        ]:
            select_size.addItem(size)
        select_size.activated[str].connect(self.setting_size)
        box_size = QVBoxLayout()
        box_size.addStretch(6)
        box_size.addWidget(QLabel('Resolution', self), 1)
        box_size.addWidget(select_size, 1)
        box_size.addStretch(3)

        box_select = QHBoxLayout()
        box_select.addLayout(box_fps, 2)
        box_select.addStretch(1)
        box_select.addLayout(box_size, 3)

        box_total = QVBoxLayout()
        box_total.addStretch(2)
        box_total.addLayout(box_select, 1)
        box_total.addStretch(1)
        box_total.addWidget(btn_start, 1)
        box_total.addStretch(2)

        self.setLayout(box_total)
        self.show()

    def setting_fps(self, text):
        self.fps = int(text)

    def setting_size(self, text):
        text = text.split()[0].split('x')
        self.size = (int(text[0]), int(text[1]))

    def start(self):
        self.game_start = True
        QCoreApplication.instance().quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    init = Init()
    app.exec_()
    del app
    if init.game_start:
        game = Game(init.size, init.fps)
        game.loop()
