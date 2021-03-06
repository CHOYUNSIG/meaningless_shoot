import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import meaningless_shoot


try:
    import pygame
    import win32gui
    import os

    rect = None
    def getWinPos(hwnd, extra):
        if win32gui.GetWindowText(hwnd) == 'meaningless: test':
            global rect
            rect = win32gui.GetWindowRect(hwnd)
        return 

    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (0, 0)
    pygame.init()
    screen = pygame.display.set_mode([300,150])
    textSurfaceObj = pygame.font.Font('meaningless_data/font/OpenSans-Bold.ttf', 32).render('loading...', True, (255,255,255), (0,0,0))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (100, 30)
    screen.blit(textSurfaceObj, textRectObj)
    pygame.display.set_caption("meaningless: test")
    pygame.display.flip()
    win32gui.EnumWindows(getWinPos, None)
    pygame.quit()

    meaningless_shoot.windowPos_x_c = -rect[0]
    meaningless_shoot.windowPos_y_c = -rect[1]
except:
    meaningless_shoot.windowPos_x_c = 10
    meaningless_shoot.windowPos_y_c = 35


class initApp(QWidget):
    def __init__(self):
        super().__init__()
        self.game_start = False
        self.initUI()
    def initUI(self):
        self.setWindowTitle('meaningless: settings')
        self.resize(300, 150)
        sqr = self.frameGeometry()
        sqr.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(sqr.topLeft())
        
        btn_start = QPushButton('&Start', self)
        btn_start.clicked.connect(self.start)

        label_fps =  QLabel('FPS', self)
        select_fps = QComboBox(self)
        for i in range(30,301,10): select_fps.addItem('%d'%i)
        select_fps.setCurrentText('60')
        select_fps.activated[str].connect(self.setting_fps)
        box_fps = QVBoxLayout()
        box_fps.addStretch(6)
        box_fps.addWidget(label_fps, 1)
        box_fps.addWidget(select_fps, 1)
        box_fps.addStretch(3)

        label_size =  QLabel('Resolution', self)
        select_size = QComboBox(self)
        select_size.addItem('640x480 (4:3)')
        select_size.addItem('960x720 (4:3)')
        select_size.addItem('1200x900 (4:3)')
        select_size.addItem('853x480 (16:9)')
        select_size.addItem('1280x720 (16:9)')
        select_size.addItem('1600x900 (16:9)')
        select_size.addItem('768x480 (16:10)')
        select_size.addItem('1152x720 (16:10)')
        select_size.addItem('1440x900 (16:10)')
        select_size.activated[str].connect(self.setting_size)
        box_size = QVBoxLayout()
        box_size.addStretch(6)
        box_size.addWidget(label_size, 1)
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
        fps = int(text)
        meaningless_shoot.fps = fps
    def setting_size(self, text):
        text = text.split()
        text = text[0].split('x')
        meaningless_shoot.size = [int(text[0]), int(text[1])]
    def start(self):
        self.game_start = True
        meaningless_shoot.windowPos_x = self.frameGeometry().center().x() - meaningless_shoot.size[0]//2
        if meaningless_shoot.windowPos_x < 0: meaningless_shoot.windowPos_x = meaningless_shoot.windowPos_x_c
        meaningless_shoot.windowPos_y = self.frameGeometry().center().y() - meaningless_shoot.size[1]//2
        if meaningless_shoot.windowPos_y < 0: meaningless_shoot.windowPos_y = meaningless_shoot.windowPos_y_c
        QCoreApplication.instance().quit()

        

app = QApplication(sys.argv)
settingWindow = initApp()
app.exec_()
del app

if settingWindow.game_start:
    meaningless_shoot.global_var1_init()
    meaningless_shoot.game_loop()
    while 'r' in meaningless_shoot.buttons:
        print("\nreloading game\n")
        time.sleep(0.1)
        meaningless_shoot.game_loop()
