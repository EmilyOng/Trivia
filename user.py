from flask_login import UserMixin
import sqlite3

class User(UserMixin):
    def __init__ (self, id_, name, email, profile_pic="", password=""):
        self.id_ = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.password = password

    def get_id (self):
        return self.id_

    @staticmethod
    def get (user_id):
        connection = sqlite3.connect("Trivia.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM User WHERE UserID=?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return None
        user = User(id_=user[0], name=user[1], email=user[2], profile_pic=user[3], password=user[4])
        connection.close()
        return user

    @staticmethod
    def create (id_, name, email, profile_pic="", password=""):
        connection = sqlite3.connect("Trivia.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO User (UserID, Name, Email, ProfilePic, Password) VALUES (?, ?, ?, ?, ?)", (id_, name, email, profile_pic, password))
        connection.commit()
        connection.close()
