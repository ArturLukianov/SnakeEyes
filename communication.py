import socket
from constants import *
from databases import *


class Server:
    def __init__(self, database, max_connections=MAX_CONNECTIONS):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.connections = []
        self.max_connections = max_connections
        self.database = database
        self.users = UsersTable(self.database)
        self.books = BooksTable(self.database)
        self.server_running = False

    def can_approve_connection(self):
        if len(self.connections) == self.max_connections:
            return False
        return True

    def handle_connection(self, conn, addr):
        print("Connection from", addr[0], "approved")
        self.connections.append(ClientConnection(conn, addr, self))

    def start(self):
        self.server_socket.bind(('0.0.0.0', PORT))
        self.server_socket.listen(MAX_CONNECTIONS)
        self.server_running = True

        while self.server_running:
            conn, addr = self.server_socket.accept()
            try:
                self.handle_connection(conn, addr)
            except:
                pass


class ServerConnection:
    def __init__(self, ip, database):
        self.ip = ip
        self.authenticated = False
        self.connected = False
        self.username = None
        self.password = None
        self.socket = None
        self.database = database

    def send(self, request):
        self.socket.send(request.encode())

    def recv(self, length):
        buff = self.socket.recv(length).decode()
        print("<", buff)
        return buff

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.socket.connect((self.ip, PORT))
        self.send(REQUEST_CONNECT)
        print("Connected to", self.ip, PORT)
        response = self.socket.recv(1024).decode()
	response_handler = self
	
        if response == RESPONSE_CONNECT_APPROVED:
            self.connected = True
            print("Connection approved")
        elif response == RESPONSE_CONNECT_RESET:
            self.connected = False
        else:
            self.connected = False
            raise Exception("Connection failure: server returned %s" % response.decode())

    def login(self, username, password):
        if self.authenticated:
            raise Exception("Login failure: already authenticated")
        self.username = username
        self.password = password
        print("Trying to login with", self.username, self.password)
        if not self.connected:
            raise Exception("Login failure: not connected")
        self.send((REQUEST_AUTHENTICATE % (username, password)))
        response = self.socket.recv(1024).decode()
        if response == RESPONSE_AUTHENTICATE_OK:
            self.authenticated = True
            print("Logged in")
        elif response == RESPONSE_AUTHENTICATE_WRONG_CREDS:
            self.authenticated = False
            print("Wrong credentials")

    def query(self, query_filter, query_string):
        self.send(REQUEST_QUERY % (query_filter, query_string))
        response = self.socket.recv(1024).decode()
        rows = int(response.split()[1])
        print("Receiving", rows, "rows")
        table = []
        self.send(REQUEST_QUERY_WAIT)
        for i in range(rows):
            response = self.recv(1024)
            response_splitted = response.split('|')
            print("#" + str(i), response_splitted[1], response_splitted[2], response_splitted[3])
            table.append(tuple(response_splitted[1:]))
            self.send(REQUEST_QUERY_WAIT)
        return table

    def get_content(self, id):
        print("Opening", id)
        self.send(REQUEST_GET_CONTENT % id)
        length = int(self.recv(10))
        print("Recieving", length, "bytes")
        self.send(REQUEST_QUERY_WAIT)
        result = ""
        for i in range(length):
            result += self.recv(1)
        print("Got")
        return result


class ClientConnection:
    def __init__(self, client_connection, client_address, server):
        self.connected = True
        self.authenticated = False
        self.client_connection = client_connection
        self.server = server
        self.client_address = client_address
        self.handle()

    def send(self, response):
        print(self.client_address[0], "<", response)
        self.client_connection.send(response.encode())

    def recv(self, length):
        request = self.client_connection.recv(length)
        print(self.client_address[0], ">", request.decode())
        return request

    def handle(self):
        while self.connected:
            skip_send = False
            request = self.recv(1024)
            request_splitted = request.decode().split()
            response = None
            if request_splitted[0] == REQUEST_CONNECT_HEADER:
                if self.server.can_approve_connection():
                    response = RESPONSE_CONNECT_APPROVED
                else:
                    response = RESPONSE_CONNECT_RESET
            elif request_splitted[0] == REQUEST_AUTHENTICATE_HEADER:
                username = request_splitted[1]
                password = request_splitted[2]
                if self.server.users.login(username, password):
                    self.authenticated = True
                    response = RESPONSE_AUTHENTICATE_OK
                else:
                    response = RESPONSE_AUTHENTICATE_WRONG_CREDS
            elif request_splitted[0] == REQUEST_QUERY_HEADER:
                query_filter = request_splitted[1]
                query = ' '.join(request_splitted[2:])
                print("Searching by", query_filter, "for", query)
                result = self.server.books.search_by(SEARCH_FILTER[query_filter], query)
                print("Found ", len(result), "results")
                response = RESPONSE_QUERY_INFO % len(result)
                self.send(response)
                self.recv(1024)
                for row in result:
                    response = RESPONSE_QUERY_LINE % (0, row[1], row[4])
                    self.send(response)
                    self.recv(1024)
                skip_send = True
            elif request_splitted[0] == REQUEST_CONTENT_HEADER:
                id = request_splitted[1]
                print("Sending", id)
                result = self.server.books.get_content(id)[1:]
                print("Sending", len(result), "bytes")
                response = RESPONSE_CONTENT_INFO % len(result)
                self.send(response)
                self.recv(1024)
                for i in range(len(result)):
                    self.send(result[i])
                print("Sent")
                skip_send = True
            if not skip_send:
                self.send(response)
