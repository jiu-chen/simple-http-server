# -*- encoding=utf-8 -*-

# 测试TcpServer和BaseRequestHandler类的功能


import threading
import socket
import time

from server.socket_server import TCPServer
from hanlder.base_hanlder import StreamRequestHandler

from server.base_http_server import BaseHttpServer
from hanlder.base_http_handler import BaseHTTPRequestHandler


class TestBaseRequestHandler(StreamRequestHandler):

    # 具体的处理逻辑 (Echo)
    def handle(self):
        msg = self.readline()
        print('Server recv msg: ' + msg)
        time.sleep(1)   # 结果没有并发，还是一个一个处理的，因为serve_forever()中的while循环只有当前连接完全结束才结束
        self.write_content(msg)
        self.send()


# 测试SocketServer(TcpServer)
class SocketServerTest:
    def run_server(self):
        tcp_server = TCPServer(('127.0.0.1', 8888), TestBaseRequestHandler)
        tcp_server.serve_forever()

    # 客户端的具体连接逻辑
    def client_connect(self):
        client = socket.socket()
        client.connect(('127.0.0.1', 8888))
        client.send(b'Hello TCPServer\r\n')
        msg = client.recv(1024)
        print('Client recv msg -> ' + msg.decode())

    # 生成客户端
    def gen_clients(self, num):
        clients = []
        for i in range(num):
            client_thread = threading.Thread(target=self.client_connect)
            clients.append(client_thread)
        return clients

    def run(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()

        clients = self.gen_clients(10)
        for client in clients:
            client.start()

        server_thread.join()
        for client in clients:
            client.join()


# 测试HTTP handler
class BaseHTTPRequestHandlerTest:
    def run_server(self):
        BaseHttpServer(('127.0.0.1', 9999), BaseHTTPRequestHandler).serve_forever()

    def run(self):
        self.run_server()


if __name__ == '__main__':
    # SocketServerTest().run()
    BaseHTTPRequestHandlerTest().run()


