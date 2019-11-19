import sqlite3
from constants import *
import os


class Database:
    def __init__(self, path):
        self.path = path
        self.initialized = False
        if os.path.exists(self.path):
            self.initialized = True
        self.connect()
        if not self.initialized:
            self.initialize()

    def connect(self):
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()

    def initialize(self):
        pass

    def commit(self):
        self.connection.commit()


class ServerDatabase(Database):
    def initialize(self):
        self.cursor.execute(SQL_CREATE_USERS)
        self.cursor.execute(SQL_CREATE_GENRES)
        self.cursor.execute(SQL_CREATE_BOOKS)


class ClientDatabase(Database):
    def initialize(self):
        self.cursor.execute(SQL_CREATE_GENRES)
        self.cursor.execute(SQL_CREATE_BOOKS)


class Table:
    def __init__(self, database):
        self.database = database


class UsersTable(Table):
    def login(self, username, password):
        result = self.database.cursor.execute(SQL_LOGIN, (username, password)).fetchall()
        return len(result) > 0

    def signup(self, username, password, privilege):
        self.database.cursor.execute(SQL_SIGNUP, (username, password, privilege))
        self.database.commit()


class GenresTable(Table):
    def add_genre(self, title):
        self.database.cursor.execute(SQL_ADD_GENRE, title)
        self.database.commit()

    def get_title(self, id):
        return self.database.cursor.execute(SQL_GET_GENRE_TITLE, id)

    def get_id(self, title):
        return self.database.cursor.execute(SQL_GET_GENRE_ID, title)


class BooksTable(Table):
    def add_book(self, title, text, genres, author):
        self.database.cursor.execute(SQL_ADD_BOOK, (title, text, genres, author))
        self.database.commit()

    def delete_book(self, id):
        pass

    def search_by(self, filter, string):
        return self.database.cursor.execute(SQL_GET_BOOKS % filter, ('%' + string + '%',)).fetchall()

    def get_content(self, id):
        return self.database.cursor.execute(SQL_GET_CONTENT, (id,)).fetchone()[0]
