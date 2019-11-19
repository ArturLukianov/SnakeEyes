from constants import *
from communication import Server, ClientConnection
from book_translator import *
from databases import ServerDatabase
import os

new_db = False

if not os.path.exists(DEFAULT_SERVER_DB_PATH):
    new_db = True
database = ServerDatabase(DEFAULT_SERVER_DB_PATH)
server = Server(database)
if new_db:
    server.users.signup('admin', 'admin', 0)
    with open('vlastelin.txt', encoding='utf-8') as book:
        server.books.add_book('Lipsum', book.read(), 0, '???')
server.start()
