from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5.Qt import QMessageBox
from constants import *


class LoginWindow(QMainWindow):
    def __init__(self, server_connection):
        super().__init__()
        uic.loadUi('client_ui_login.ui', self)
        self.server_connection = server_connection
        self.show()
        self.search_window = SearchWindow(server_connection)
        self.connectButton.clicked.connect(self.connect_to_server)

    def connect_to_server(self):
        if not self.server_connection.connected:
            self.server_connection.connect()
        if not self.server_connection.authenticated:
            username = self.usernameInput.text()
            password = self.passwordInput.text()
            self.server_connection.login(username, password)
            if self.server_connection.authenticated:
                self.search_window.show()
                self.hide()


class Reader(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('reader.ui', self)

    def set_book(self, text):
        self.textBrowser.setText(text)


class SearchWindow(QMainWindow):
    def __init__(self, server_connection):
        super().__init__()
        self.server_connection = server_connection
        uic.loadUi('client_ui_search.ui', self)
        self.findButton.clicked.connect(self.query)
        self.tableWidget.clicked.connect(self.open_book)
        self.reader = Reader()

    def query(self):
        query_string = self.searchQuery.text()
        query_filter = REQUEST_QUERY_FILTERS[self.filterInput.currentText()]
        print("Query:", query_filter, query_string)
        result = self.server_connection.query(query_filter, query_string)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["id", "Title", "Author"])
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(result):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()

    def open_book(self, item):
        id = item.row() + 1
        self.reader.set_book(self.server_connection.get_content(id))
        self.reader.show()


