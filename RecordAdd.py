from PyQt5.QtWidgets import QDialog, QLabel, QPushButton
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtGui
import sqlite3
import shutil
import os
from WindowAdd import Ui_WindowAdd


class RecordAdd(QDialog, Ui_WindowAdd):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.BtnAdd.clicked.connect(self.checkConditions)
        self.PhotoAdd.clicked.connect(self.selectPhoto)
        self.calendar.selectionChanged.connect(self.updateDate)
        self.Name.textChanged.connect(self.changeColor)
        self.Period.currentIndexChanged.connect(self.changeColor)
        self.BtnAdd.setStyleSheet("background-color: green;")

    def formQuery(self, title, finishdate, rank, comment, photo=""):
        if photo == "":
            return f"""
            INSERT INTO Targets (Title, FinishDate, Rank, Comment)
            VALUES ('{title}', '{finishdate}','{rank}','{comment}')    ;    
            """
        else:
            currentPath = os.getcwd() + "/photos"
            newPath = shutil.copy(photo, currentPath)
            return f"""
                        INSERT INTO Targets (Title, FinishDate, Rank, Comment, Photo)
                        VALUES ('{title}', '{finishdate}','{rank}','{comment}', '{newPath}');    
                        """

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

    def queryAdd(self):
        CondFP = True
        title = self.Name.text()
        finishDate = self.calendar.selectedDate().toString()
        rank = self.Period.currentText()
        comment = self.Comment.text()
        try:
            FilePath = self.FilePath
        except Exception:
            CondFP = False
        Connection = sqlite3.connect("Notifications.db")
        Cursor = Connection.cursor()
        if CondFP:
            Cursor.execute(self.formQuery(title, finishDate, rank, comment, self.FilePath))

        else:
            Cursor.execute(self.formQuery(title, finishDate, rank, comment))
        Connection.commit()
        self.getConfirm()
        self.dialogConfirm.show()
        self.setDisabled(True)
        self.dialogConfirm.exec_()
        self.close()

    def selectPhoto(self):
        self.FilePath = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Все файлы (*);;Картинка (*.jpg);;Картинка (*.jpg)')[0]
        self.PhotoAdd.setText(self.PhotoAdd.text() + "\n" + self.FilePath.split("/")[-1])

    def checkConditions(self):
        cond = True
        if self.Name.text() == "":
            cond = False
            self.Name.setStyleSheet("background-color: red;")
        if self.Period.currentIndex() == 0:
            cond = False
            self.Period.setStyleSheet("background-color: red;")
        if cond:
            self.queryAdd()

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
