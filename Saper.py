from random import randint
import time
import sys
from PyQt5 import QtMultimedia, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QMenuBar, QMenu, QAction, QTableWidgetItem
from PyQt5.QtWidgets import QPushButton, QLabel, QSpinBox, QButtonGroup, QLCDNumber, QLineEdit, QTableWidget
from PIL import Image
import csv


class MinesExeption(Exception):
    pass


class FieldButton(QPushButton):
    def __init__(self, MW):
        super().__init__(MW)
        self.host = MW
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.host.infw.saper.open(self.x, self.y)
        elif event.button() == Qt.RightButton:
            self.host.infw.saper.flag(self.x, self.y)
        self.host.infw.saper.display()


class GetInfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(533, 314, 380, 140)
        self.setWindowTitle('Окно для ввода информации об игре')
        # Ширина поля
        self.get_x = QSpinBox(self)
        self.get_x.setMinimum(9)
        self.get_x.setValue(20)
        self.get_x.setMaximum(30)
        self.get_x.resize(40, 20)
        self.get_x.move(250, 10)
        self.x_lable = QLabel('Введите ширину поля', self)
        self.x_lable.move(20, 10)
        # Высота поля
        self.get_y = QSpinBox(self)
        self.get_y.setMinimum(9)
        self.get_y.setMaximum(24)
        self.get_y.setValue(15)
        self.get_y.resize(40, 20)
        self.get_y.move(250, 40)
        self.y_lable = QLabel('Введите высоту поля', self)
        self.y_lable.move(20, 40)
        # Колличество мин
        self.get_m = QSpinBox(self)
        self.get_m.setMinimum(10)
        self.get_m.setValue(20)
        self.get_m.setMaximum(576)
        self.get_m.resize(40, 20)
        self.get_m.move(250, 70)
        self.m_lable = QLabel('Введите количество мин', self)
        self.m_lable.move(20, 70)
        # Ярлык для ошибки при неправильном вводе колличества мин
        self.errlbl = QLabel(self)
        self.errlbl.move(20, 92)
        self.errlbl.resize(380, 20)
        # Кнопка для начала игры
        self.okbtn = QPushButton('Начать игру', self)
        self.okbtn.resize(100, 25)
        self.okbtn.move(100, 110)
        self.okbtn.clicked.connect(self.getinfobtn)

    def getinfobtn(self):
        try:
            self.getinfo()
            self.mines = []
            self.saperwindow = SaperWindow(self.get_x.value(), self.get_y.value(), self.get_m.value(), self)
            self.saper = Saper(self.get_x.value(), self.get_y.value(), self.get_m.value(), True, self.saperwindow)
            self.saperwindow.show()
            self.close()
        except MinesExeption:
            self.errlbl.setText(f'Колличество мин должно быть между {min(self.get_x.value(), self.get_y.value(), 10)}'
                                f' и {int(self.get_x.value() * self.get_y.value() * 0.8)}')

    def getinfo(self):
        if self.get_m.value() > int(self.get_x.value() * self.get_y.value() * 0.8):
            raise MinesExeption


class SaperWindow(QMainWindow):
    def __init__(self, wight, height, mines, infw):
        super().__init__()
        self.infw = infw
        self.initUI(wight, height, mines)

    def initUI(self, wight, height, mines):
        self.setGeometry(672 - wight * 10, 370 - height * 10, (wight + 2) * 20, (height + 5) * 20)
        self.setWindowTitle('Сапер')
        self.load_mp3()
        # Меню
        self.createmenu()
        # Мин осталось
        self.minesleft = QLCDNumber(self)
        self.minesleft.move((wight - 2) * 20, 37)
        self.minesleft.resize(60, 30)
        self.minesleft.display(mines)
        self.mllbl = QLabel('Мин осталось:', self)
        self.mllbl.move((wight - 3) * 20, 15)
        # Времени прошло
        self.starttime = time.time()
        self.timer = self.startTimer(10, timerType=Qt.CoarseTimer)
        self.time = QLCDNumber(self)
        self.time.move(20, 37)
        self.time.resize(60, 30)
        self.timelbl = QLabel('Время:', self)
        self.timelbl.move(20, 15)
        # Поле с кнопками
        self.btns = QButtonGroup(self)
        for i in range(wight):
            for j in range(height):
                self.btn = FieldButton(self)
                self.btn.resize(18, 18)
                self.btn.move(20 * i + 20, 20 * j + 75)
                self.btn.x, self.btn.y = i + 1, j + 1
                self.btn.setStyleSheet("background-color: #4682B4")
                self.btns.addButton(self.btn)

    def createmenu(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)
        self.createactions()
        self.editMenu = self.menuBar.addMenu("Игра")
        self.editMenu.addAction(self.newgameAction)
        self.editMenu.addAction(self.restartAction)
        self.editMenu.addAction(self.resultAction)
        self.editMenu.addAction(self.infoAction)
        self.editMenu.addAction(self.exitAction)

    def timerEvent(self, event):
        self.time.display(int(time.time() - self.starttime))

    def createactions(self):
        self.newgameAction = QAction("Новая игра", self)
        self.newgameAction.triggered.connect(self.newgame)
        self.restartAction = QAction("Перезапустить", self)
        self.restartAction.triggered.connect(self.restart)
        self.exitAction = QAction("Выход", self)
        self.exitAction.triggered.connect(self.exit)
        self.resultAction = QAction("Список результатов", self)
        self.resultAction.triggered.connect(self.result)
        self.infoAction = QAction("Об игре", self)
        self.infoAction.triggered.connect(self.info)

    def result(self):
        self.resultwindow = resultwidget()
        self.resultwindow.show()

    def info(self):
        self.infowindow = infowidget()
        self.infowindow.show()

    def exit(self):
        self.killTimer(self.timer)
        self.close()

    def restart(self):
        if self.infw.saper.mines:
            self.close()
            self.killTimer(self.timer)
            self.mines = self.infw.saper.mines
            self.saperwindow = SaperWindow(self.infw.saper.x, self.infw.saper.y, self.infw.saper.m, self)
            self.saper = Saper(self.infw.saper.x, self.infw.saper.y, self.infw.saper.m, False, self.saperwindow)
            self.saperwindow.show()
        else:
            self.starttime = time.time()

    def newgame(self):
        self.close()
        self.killTimer(self.timer)
        self.NewInfoWindow = GetInfoWindow()
        self.NewInfoWindow.show()

    def load_mp3(self):
        win = QtCore.QUrl.fromLocalFile('/home/aydar/PycharmProjects/SaperProject/sapersounds/win.mp3')
        lose = QtCore.QUrl.fromLocalFile('/home/aydar/PycharmProjects/SaperProject/sapersounds/lose.mp3')
        wsound = QtMultimedia.QMediaContent(win)
        lsound = QtMultimedia.QMediaContent(lose)
        self.wplayer = QtMultimedia.QMediaPlayer()
        self.wplayer.setMedia(wsound)
        self.lplayer = QtMultimedia.QMediaPlayer()
        self.lplayer.setMedia(lsound)


class Saper:
    def __init__(self, x, y, m, res, sw):
        self.x = x
        self.y = y
        self.m = m
        self.minesleft = m
        self.mines = sw.infw.mines
        self.SW = sw
        self.MakeField()
        self.first = res

    def MakeField(self):
        self.field = [[' ' for j in range(self.y + 2)] for i in range(self.x + 2)]
        self.field[0] = ['+'] * (self.y + 2)
        for i in range(self.x):
            self.field[i + 1][0] = '+'
            self.field[i + 1][self.y + 1] = '+'
        self.field[self.x + 1] = ['+'] * (self.y + 2)

    def setmines(self, x, y):
        self.mines = [(randint(1, self.x), randint(1, self.y)) for i in range(self.m)]
        while (x, y) in self.mines:
            self.mines = [(randint(1, self.x), randint(1, self.y)) for i in range(self.m)]

    def display(self):
        for btn in self.SW.btns.buttons():
            if self.field[btn.x][btn.y] == 'checked':
                btn.setStyleSheet("background-color: #FFFFE0")
                btn.setEnabled(False)
            elif self.field[btn.x][btn.y].isdigit():
                btn.setStyleSheet("background-color: #FFFFE0")
                btn.setText(f'{self.field[btn.x][btn.y]}')
                btn.setEnabled(False)
            elif self.field[btn.x][btn.y] == 'mine':
                btn.setStyleSheet("background-color: #FF1F1F")
                btn.setEnabled(False)
            else:
                btn.setText(f'{self.field[btn.x][btn.y]}')

    def flag(self, x, y):
        if self.field[x][y] == 'F':
            self.minesleft += 1
            self.SW.minesleft.display(self.minesleft)
            self.field[x][y] = '?'
        elif self.field[x][y] == ' ':
            self.SW.load_mp3()
            self.minesleft -= 1
            self.SW.minesleft.display(self.minesleft)
            self.field[x][y] = 'F'
        elif self.field[x][y] == '?':
            self.field[x][y] = ' '
        self.display()

    def open(self, x, y):
        if self.first:
            self.setmines(x, y)
            self.first = False
        if self.field[x][y] in ('F', '?'):
            pass
        elif (x, y) in self.mines:
            for i in self.mines:
                self.field[i[0]][i[1]] = 'mine'
            self.lose()
        else:
            neibours = self.check(x, y)[:]
            if len(neibours) == 9:
                self.field[x][y] = 'checked'
                for neibour in neibours:
                    if 0 < neibour[0] <= self.x and 0 < neibour[1] <= self.y\
                            and self.field[neibour[0]][neibour[1]] != 'checked':
                        self.open(neibour[0], neibour[1])
            else:
                self.field[x][y] = f'{9 - len(neibours)}'
            self.wincheck()

    def check(self, x, y):
        neibours = []
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if (i, j) not in self.mines:
                    neibours.append((i, j))
        return neibours

    def wincheck(self):
        for btn in self.SW.btns.buttons():
            if self.field[btn.x][btn.y] == ' ' and (btn.x, btn.y) not in self.mines:
                return 0
        self.win()

    def lose(self):
        self.SW.killTimer(self.SW.timer)
        self.SW.lplayer.play()
        self.event = 'Вы проиграли'
        self.endW = EndWindow(self)
        self.endW.show()

    def win(self):
        self.SW.killTimer(self.SW.timer)
        self.SW.wplayer.play()
        self.event = 'Вы выиграли!'
        self.time = int(time.time() - self.SW.starttime)
        self.endW = EndWindow(self)
        self.endW.show()


class EndWindow(QWidget):
    def __init__(self, saper):
        super().__init__()
        self.initUI(saper)

    def initUI(self, saper):
        self.saper = saper
        self.setWindowTitle('')
        self.setGeometry(533, 314, 300, 150)
        if self.saper.event == 'Вы выиграли!':
            self.resultlbl = QLabel(self.saper.event, self)
            self.resultlbl.move(80, 20)
            self.timelbl = QLabel(f'Ваше время:{self.saper.time}', self)
            self.timelbl.move(80, 40)
            self.result = 5 * self.saper.x * self.saper.y * self.saper.m // self.saper.time
            self.resultlbl = QLabel(f'Итоговый результат:{self.result}', self)
            self.resultlbl.move(80, 60)
            self.namelbl = QLabel('Введите ваше имя', self)
            self.namelbl.move(10, 80)
            self.name = QLineEdit(self)
            self.name.move(150, 80)
        else:
            self.resultlbl = QLabel(self.saper.event, self)
            self.resultlbl.move(100, 20)
        self.exitbtn = QPushButton('Выйти', self)
        self.exitbtn.resize(80, 30)
        self.exitbtn.move(10, 110)
        self.exitbtn.clicked.connect(self.exit)
        self.restartbtn = QPushButton('Переиграть', self)
        self.restartbtn.resize(80, 30)
        self.restartbtn.move(110, 110)
        self.restartbtn.clicked.connect(self.restart)
        self.newgamebtn = QPushButton('Новая игра', self)
        self.newgamebtn.resize(80, 30)
        self.newgamebtn.move(210, 110)
        self.newgamebtn.clicked.connect(self.newgame)

    def exit(self):
        if self.saper.event == 'Вы выиграли!':
            self.winner()
        self.saper.SW.close()
        self.close()

    def restart(self):
        if self.saper.event == 'Вы выиграли!':
            self.winner()
        self.saper.SW.close()
        self.close()
        self.mines = self.saper.mines
        self.saperwindow = SaperWindow(self.saper.x, self.saper.y, self.saper.m, self)
        self.saper = Saper(self.saper.x, self.saper.y, self.saper.m, False, self.saperwindow)
        self.saperwindow.show()

    def newgame(self):
        if self.saper.event == 'Вы выиграли!':
            self.winner()
        self.saper.SW.close()
        self.close()
        self.NewInfoWindow = GetInfoWindow()
        self.NewInfoWindow.show()

    def winner(self):
        try:
            with open('tierlist.csv', encoding="utf8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
                self.top = list(reader) + [{'Имя': self.name.text(),
                                    'Результат': self.result,
                                    'Время': self.saper.time,
                                    'Ширина поля': self.saper.x,
                                    'Высота поля': self.saper.y,
                                    'Колличество мин': self.saper.m}]
                self.top.sort(key=lambda x: int(x['Результат']), reverse=True)
                csvfile.close()
        except:
            self.top = [{'Имя': self.name.text(),
                        'Результат': self.result,
                        'Время': self.saper.time,
                        'Ширина поля': self.saper.x,
                        'Высота поля': self.saper.y,
                        'Колличество мин': self.saper.m}]
        with open('tierlist.csv', 'w', newline='', encoding="utf8") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=list(self.top[0].keys()),
                delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            writer.writerows(self.top)
            csvfile.close()
        self.resultwindow = resultwidget()
        self.resultwindow.show()


class infowidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Об игре')
        self.setGeometry(300, 300, 300, 200)
        self.im = Image.open('sapericon.ico')
        self.im = self.im.resize((100, 100))
        self.im.save('inficon.png')
        self.pixmap = QPixmap('inficon.png')
        self.image = QLabel(self)
        self.image.move(100, 10)
        self.image.resize(100, 100)
        self.image.setPixmap(self.pixmap)
        self.lbl = QLabel('Класическая игра в сапера\nРазработал Байсуваков\nАйдар Галинурович\n', self)
        self.lbl.move(0, 110)


class resultwidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Рейтинг')
        self.setGeometry(300, 300, 600, 600)
        try:
            with open('tierlist.csv', encoding="utf8") as csvfile:
                self.reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                self.title = next(self.reader)
                self.tableWidget = QTableWidget(self)
                self.tableWidget.resize(600, 600)
                self.tableWidget.setColumnCount(len(self.title))
                self.tableWidget.setHorizontalHeaderLabels(self.title)
                self.tableWidget.setRowCount(0)
                for i, row in enumerate(self.reader):
                    self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                    for j, elem in enumerate(row):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(elem))
            self.tableWidget.resizeColumnsToContents()
            csvfile.close()
        except:
            self.lbl = QLabel('Список результатов пуст', self)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def game():
    app = QApplication(sys.argv)
    InfoWindow = GetInfoWindow()
    InfoWindow.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())


game()