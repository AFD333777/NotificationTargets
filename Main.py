import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, \
    QPushButton, QSystemTrayIcon, QStyle, QAction, QMenu
from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui
from WindowBasic import Ui_MainWindow
from Database import Database
from RecordAdd import RecordAdd
import sqlite3
import threading
import datetime as dt
import platform
import win10toast


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db = Database()
        self.connection = sqlite3.connect("Notifications.db")
        self.cursor = self.connection.cursor()
        self.setFixedSize(1200, 800)
        self.btn_add.clicked.connect(self.recordAdd)
        self.btn_delete.clicked.connect(self.recordDelete)
        self.viewDay()
        self.viewRecord()
        self.calendar.selectionChanged.connect(self.viewDay)
        self.Targets.currentIndexChanged.connect(self.viewRecord)
        self.btnOpenPhoto.clicked.connect(self.openPhoto)
        self.createFolderPhotos()
        self.condTray = False
        self.condQuit = False
        first = threading.Thread(target=self.checkTime)
        first.start()

    def getNotification(self, title, message):
        plt = platform.system()
        if plt == "Darwin":
            command = '''
            osascript -e 'display notification "{message}" with title "{title}"'
            '''
        elif plt == "Linux":
            command = f'''
            notify-send "{title}" "{message}"
            '''
        elif plt == "Windows":
            win10toast.ToastNotifier().show_toast(title, message)
            return
        else:
            return
        os.system(command)

    def checkTime(self):
        while True:
            if self.getCondQuit():
                sys.exit()
            if dt.datetime.now().strftime("%M:%S") == "00:00":
                self.getNotification("Notification Targets", "Зайдите в приложение")

    def changeCondQuit(self):
        self.condQuit = True

    def getCondQuit(self):
        return self.condQuit

    def getOverlay(self):
        if not self.condTray:
            self.condTray = True
            self.overlay = QSystemTrayIcon(self.style().standardIcon(QStyle.SP_ComputerIcon), self)
            showApp = QAction("Открыть", self)
            hideApp = QAction("Скрыть", self)
            quitApp = QAction("Закрыть", self)
            showApp.triggered.connect(self.show)
            hideApp.triggered.connect(self.hide)
            quitApp.triggered.connect(QApplication.quit)
            quitApp.triggered.connect(self.changeCondQuit)
            trayMenu = QMenu()
            trayMenu.addAction(showApp)
            trayMenu.addAction(hideApp)
            trayMenu.addAction(quitApp)
            self.overlay.setContextMenu(trayMenu)
            self.overlay.show()

    def recordAdd(self):
        self.WindowAdd = RecordAdd(self)
        self.WindowAdd.show()
        self.setDisabled(True)
        self.WindowAdd.exec_()
        self.setDisabled(False)
        self.viewDay()
        self.viewRecord()

    def recordDelete(self):
        try:
            self.db.queryDel(self.record[0])
            self.viewDay()
            self.viewRecord()
            self.getConfirm()
            self.dialogConfirm.show()
            self.setDisabled(True)
            self.dialogConfirm.exec_()
            self.setDisabled(False)
        except Exception:
            self.labelError.setText("Не выбрана запись для удаления!")
            self.labelError.resize(self.labelError.sizeHint())
            self.labelError.setStyleSheet("background-color:red;")
            self.labelError.show()

    def openPhoto(self):
        try:
            name = self.record[-1]
            os.startfile(name)
        except TypeError:
            self.labelError.setText("Фото отсутсвует")
            self.labelError.resize(self.labelError.sizeHint())
            self.labelError.setStyleSheet("background-color:red;")
            self.labelError.show()

    def viewDay(self):
        self.clearRecord()
        self.calendar.setSelectedDate(self.calendar.selectedDate())
        date = self.calendar.selectedDate().toString()
        data = self.cursor.execute(f"""SELECT * FROM Targets WHERE FinishDate='{date}' ORDER BY Title ASC""").fetchall()
        if len(data) != 0:
            [self.Targets.addItem(elem[1]) for elem in data]
        else:
            self.Targets.addItem("Данные отсутствуют!")

    def viewRecord(self):
        self.labelError.hide()
        date = self.calendar.selectedDate().toString()
        data = self.cursor.execute(
            f"""SELECT * FROM Targets WHERE FinishDate='{date}' ORDER BY Title ASC""").fetchall()
        if len(data) != 0:
            self.undisableButtons()
            self.labelError.hide()
            self.record = data[self.Targets.currentIndex()]
            self.labelComment.setText(self.record[-2])
            if not (self.record[-1] is None):
                pixmap = QPixmap(self.record[-1])
                self.labelPhoto.setPixmap(pixmap.scaled(611, 311))
            else:
                pixmap = QPixmap()
                self.labelPhoto.setPixmap(pixmap)
        else:
            self.labelError.setText("Не найдено записей")
            self.labelError.resize(self.labelError.sizeHint())
            self.labelError.setStyleSheet("background-color:red;")
            self.labelError.show()
            self.disableButtons()

    def undisableButtons(self):
        self.btn_delete.setDisabled(False)
        self.btnOpenPhoto.setDisabled(False)

    def disableButtons(self):
        self.btn_delete.setDisabled(True)
        self.btnOpenPhoto.setDisabled(True)

    def getConfirm(self):
        self.dialogConfirm = QDialog()
        self.dialogConfirm.setWindowTitle("Уведомление")
        self.dialogConfirm.setFixedSize(300, 100)
        label = QLabel(self.dialogConfirm)
        label.setText("Успешно удалили запись!")
        btn = QPushButton(self.dialogConfirm)
        btn.setText("ОК")
        btn.setStyleSheet("background-color:green;")
        btn.move(100, 50)
        btn.resize(btn.sizeHint())
        font = QtGui.QFont()
        font.setPointSize(12)
        label.setFont(font)
        label.resize(label.sizeHint())
        label.move(25, 25)
        btn.clicked.connect(self.closeDialogConfirm)

    def closeDialogConfirm(self):
        self.dialogConfirm.close()

    def clearRecord(self):
        self.Targets.clear()
        self.labelComment.clear()
        self.labelPhoto.clear()

    def createFolderPhotos(self):
        if not os.path.exists("photos"):
            path = os.getcwd() + "/photos"
            os.mkdir(path)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.getOverlay()
        self.overlay.showMessage("Notification Targets",
                                 "Приложение помещено в оверлей",
                                 QSystemTrayIcon.Information, 10)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainApp = Main()
    MainApp.show()
    app.exec_()
