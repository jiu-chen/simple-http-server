# -*- encoding=utf-8 -*-

from hanlder.base_http_handler import BaseHTTPRequestHandler
from urllib import parse
import os
import json


RESOURCES_PATH = os.path.join(os.path.abspath(os.path.dirname(__name__)), '../resources')


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, server, request, client_address):
        BaseHTTPRequestHandler.__init__(self, server, request, client_address)

    def do_GET(self):
        found, resource_path = self.get_resources(self.path)
        if not found:
            self.write_error(404)
            # self.send()
        else:
            with open(resource_path, 'rb') as f:
                fs = os.fstat(f.fileno())
                # 获取文件的长度
                flength = str(fs[6])
                self.write_response(200)
                self.write_header('Content-Length', flength)
                # 避免跨域问题 未生效？
                self.write_header('Access-Control-Allow-Origin', 'http://%s:%d' %
                                  (self.server.server_address[0], self.server.server_address[1]))
                self.end_response_headers()
                while True:
                    buf = f.read(1024)
                    if not buf:
                        break
                    self.write_content(buf)
                # self.send()  # 已有base_http_handler.py line 32 self.send()

    # 判断并获取资源
    def get_resources(self, path):
        '''  console ##
        from urllib import parse
        parse.urlparse('/index.html')
        ParseResult(scheme='', netloc='', path='/index.html', params='', query='', fragment='')
        parse.urlparse('/index.html/page=1&count=10')
        ParseResult(scheme='', netloc='', path='/index.html/page=1&count=10', params='', query='', fragment='')
        '''
        url_result = parse.urlparse(path)
        resource_path = url_result[2]
        if resource_path.startswith('/'):
            resource_path = resource_path[1:]
        resource_path = os.path.join(RESOURCES_PATH, resource_path)
        # print('response_path is' + resource_path)
        if os.path.exists(resource_path) and os.path.isfile(resource_path):
            return True, resource_path
        else:
            return False, resource_path

    def do_POST(self):
        # 账户和密码的校验
        # 从请求取出数据
        body = json.loads(self.body)
        print(body)
        username = body['username']
        password = body['password']
        # 数据校验
        if username == 'user' and password == '123':
            response = {'message': 'success', 'code': 0}
        else:
            response = {'message': 'failed', 'code': -1}
        response = json.dumps(response)
        # 组成应答报文
        self.write_response(200)
        self.write_header('Content-Length', len(response))
        # 避免跨域问题  not work?
        self.write_header('Access-Control-Allow-Origin', 'http://%s:%d' %
                          (self.server.server_address[0], self.server.server_address[1]))
        self.end_response_headers()
        self.write_content(response)

