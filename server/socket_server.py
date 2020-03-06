# -*- encoding=utf-8 -*-

import socket
import threading


class TCPServer:

    # 构造函数
    def __init__(self, server_address, handler_class):
        self.server_address = server_address
        self.HandlerClass = handler_class
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET IPv4
        self.is_shutdown = False

    # 启动
    def serve_forever(self):
        self.socket.bind(self.server_address)
        self.socket.listen(10)
        # while True:
        while not self.is_shutdown:   # 如果服务器没有被关闭
            # 1. 接受请求
            request, client_address = self.get_request()
            # 2. 处理请求
            try:
                # self.process_request(request, client_address)
                # 使用多线程
                self.process_request_multithread(request, client_address)
            except Exception as e:
                print('error is ' + e)
            # finally:

    # 接受请求
    def get_request(self):
        return self.socket.accept()

    # 处理请求
    def process_request(self, request, client_address):
        handler = self.HandlerClass(self, request, client_address)
        handler.handle()
        # 3. 关闭连接, 使用多线程的话，需要在这里关闭连接。即把关闭操作放在线程内完成
        self.close_request(request)

    # 多线程处理请求
    def process_request_multithread(self, equest, client_address):
        t = threading.Thread(target=self.process_request, args=(equest, client_address))
        t.start()

    # 关闭请求
    def close_request(self, request):
        request.shutdown(socket.SHUT_WR)
        request.close()

    # 关闭server
    def shutdown(self):
        self.is_shutdown = True
