# -*- encoding=utf-8 -*-

from server.base_http_server import BaseHttpServer
from hanlder.simple_http_handler import SimpleHTTPRequestHandler

# 测试simple_http_handler下的do_Get()方法


class SimpleHttpServer(BaseHttpServer):
    def __init__(self, server_address, handler_class):
        self.server_name = 'SimpleHTTPServer'
        self.version = 'v0.2'
        BaseHttpServer.__init__(self, server_address, handler_class)


if __name__ == '__main__':
    SimpleHttpServer(('127.0.0.1', 8888), SimpleHTTPRequestHandler).serve_forever()