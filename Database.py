import sqlite3

import os
import shutil


class Database:
    def __init__(self):
        if not os.path.exists("Notifications.db"):
            self.connection = sqlite3.connect("Notifications.db")
            self.cursor = self.connection.cursor()
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS "Targets"
            (
            'id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Title' TEXT NOT NULL,
            'FinishDate' STRING NOT NULL,
            'Rank' TEXT NOT NULL,
            'Comment' TEXT,
            'Photo' TEXT
            );
            """)
            self.connection.commit()

    def queryAdd(self, title, finishDate, rank, comment, filePath):
        connection = sqlite3.connect("Notifications.db")
        cursor = connection.cursor()
        if filePath == "":
            cursor.execute("""INSERT INTO Targets (Title, FinishDate, Rank, Comment)
            VALUES (?, ?, ?, ?);""", (title, finishDate, rank, comment))
        else:
            currentPath = os.getcwd() + "/photos"
            shutil.copy(filePath, currentPath)
            cursor.execute("""INSERT INTO Targets (Title, FinishDate, Rank, Comment, Photo)
            VALUES (?, ?, ?, ?, ?); """, (title, finishDate, rank, comment, currentPath))
        connection.commit()

    def queryDel(self, idRecord):
        connection = sqlite3.connect("Notifications.db")
        cursor = connection.cursor()
        cursor.execute("""
                    DELETE FROM Targets 
                    WHERE 
                    id = ?;        
                    """, (idRecord,))
        connection.commit()
