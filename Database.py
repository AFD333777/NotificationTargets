import sqlite3

import os


class Database:
    def __init__(self):
        if not os.path.exists("Notifications.db"):
            self.Connection = sqlite3.connect("Notifications.db")
            self.Cursor = self.Connection.cursor()
            self.Connection.commit()
            self.Cursor.execute("""
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
