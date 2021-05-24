from PyQt5.QtWidgets import QDialog, QLabel, QPushButton
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtGui
import sqlite3
from WindowAdd import Ui_WindowAdd
from Database import Database


class RecordAdd(QDialog, Ui_WindowAdd):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(1200, 800)
        self.db = Database()
        self.connection = sqlite3.connect("Notifications.db")
        self.cursor = self.connection.cursor()
        self.updateDate()
        self.BtnAdd.clicked.connect(self.checkConditions)
        self.PhotoAdd.clicked.connect(self.selectPhoto)
        self.calendar.selectionChanged.connect(self.updateDate)
        self.Name.textChanged.connect(self.changeColor)
        self.Period.currentIndexChanged.connect(self.changeColor)

    def getConfirm(self):
        self.dialogConfirm = QDialog()
        self.dialogConfirm.setWindowTitle("Уведомление")
        self.dialogConfirm.setFixedSize(300, 100)
        label = QLabel(self.dialogConfirm)
        label.setText("Успешно добавили запись!")
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

    def selectPhoto(self):
        self.FilePath = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Все файлы (*);;Картинка (*.jpg);;Картинка (*.jpg)')[0]
        self.PhotoAdd.setText(self.PhotoAdd.text() + "\n" + self.FilePath.split("/")[-1])

    def checkConditions(self):
        cond = True
        FilePath = ""
        if self.Name.text() == "":
            cond = False
            self.Name.setStyleSheet("background-color: red;")
        if self.Period.currentIndex() == 0:
            cond = False
            self.Period.setStyleSheet("background-color: red;")
        if cond:
            try:
                FilePath = self.FilePath
            except Exception:
                pass
            self.db.queryAdd(self.Name.text(), self.calendar.selectedDate().toString(),
                             self.Period.currentText(), self.Comment.text(), FilePath)
            self.getConfirm()
            self.dialogConfirm.show()
            self.setDisabled(True)
            self.dialogConfirm.exec_()
            self.close()

    def updateDate(self):
        self.labelDate.setText("Дата окончания: " + self.calendar.selectedDate().toString())
        self.labelDate.resize(self.labelDate.sizeHint())

    def changeColor(self):
        if self.sender() == self.Name:
            self.Name.setStyleSheet("background-color: white;")
        if self.sender() == self.Period:
            self.Period.setStyleSheet("background-color: white;")

    def closeEvent(self, event):
        self.close()
