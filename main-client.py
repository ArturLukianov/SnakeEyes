import sys
from PyQt5.QtWidgets import QApplication
from communication import ServerConnection
from databases import ClientDatabase
from constants import *
from client_ui import *

database = ClientDatabase(DEFAULT_CLIENT_DB_PATH)
server_connection = ServerConnection("127.0.0.1", database)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_widget = LoginWindow(server_connection)
    login_widget.show()
    sys.exit(app.exec_())
