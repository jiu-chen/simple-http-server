# -*- encoding=utf-8 -*-

import logging

from hanlder.base_hanlder import StreamRequestHandler
from utils import date_time_string

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class BaseHTTPRequestHandler(StreamRequestHandler):
    def __init__(self, server, request, client_address):
        self.method = None
        self.path = None
        self.version = None
        self.headers = None
        self.body = None
        self.request_line = None
        StreamRequestHandler.__init__(self, server, request, client_address)

    # 处理请求
    def handle(self):
        try:
            # 1. 解析请求
            if not self.parse_request():
                return
            # 2. 方法执行 (GET, POST)
            method_name = 'do_' + self.method
            if not hasattr(self, method_name):
                self.write_error(404, None)
                self.send()
                return
            method = getattr(self, method_name)  # getattr() 函数用于返回一个对象属性值。
            method()  # 应答报文封装
            # 发送结果
            self.send()
        except Exception as e:
            logging.exception(e)

    # 实现 do_GET()方法
    def do_GET(self):
        msg = '<h1>Hello Client</h1>'
        self.write_response(200, 'Success')
        self.write_header('Content-Length', len(msg))
        self.end_response_headers()
        self.write_content(msg)

    # 解析请求
    def parse_request(self):
        # 1.解析请求头
        request_line = self.readline()
        self.request_line = request_line
        if not request_line:   # error: not enough values to pack.这个错误表示读取到了空行
            return
        words = request_line.split()
        # 2.请求方法，请求地址，http版本
        self.method, self.path, self.version = words

        # 3. 解析请求行
        self.headers = self.parse_headers()

        # 解析请求内容
        key = 'Content-Length'
        if key in self.headers.keys():
            # 请求内容的长度
            body_length = int(self.headers[key])
            self.body = self.read(body_length)
        return True

    # 解析头部
    def parse_headers(self):
        headers = {}
        while True:
            line = self.readline()
            # 如果是空行，表示请求头结束
            if line:
                key, value = line.split(":", 1)  # 比如Host:coding.imooc.com:xxx 会被分割成Host和coding.imooc.com:xxx
                key.split()
                value.split()
                headers[key] = value
            else:
                break
        return headers

    # 写入响应头
    def write_header(self, key, value):
        msg = '%s: %s\r\n' % (key, value)
        self.write_content(msg)

    default_http_version = 'HTTP/1.1'

    # 写入响应报文
    def write_response(self, code, msg=None):
        logging.info('%s, code: %s. ' % (self.request_line, code))
        if msg == None:
            msg = self.responses[code][0]

        # 状态行
        status_line = '%s, %d, %s\r\n' % (self.default_http_version, code, msg)
        self.write_content(status_line)

        # 应答头
        self.write_header('Server', '%s, %s' %
                          (self.server.server_name, self.server.version))
        self.write_header('Date', date_time_string())

    DEFAULT_ERROR_MESSAGE_TEMPLATE = r'''
        <head>
        <title>Error response</title>
        </head>
        <body>
        <h1>Error response</h1>
        <p>Error code %(code)d.
        <p>Message: %(message)s.
        <p>Error code explanation: %(code)s = %(explain)s.
        </body>
    '''

    responses = {
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols',
              'Switching to new protocol; obey Upgrade header'),

        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No Content', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),

        300: ('Multiple Choices',
              'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not Modified',
              'Document has not changed since given time'),
        305: ('Use Proxy',
              'You must use proxy specified in Location to access this '
              'resource.'),
        307: ('Temporary Redirect',
              'Object moved temporarily -- see URI list'),

        400: ('Bad Request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment Required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this resource.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with '
                                               'this proxy before proceeding.'),
        408: ('Request Timeout', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone',
              'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable',
              'Cannot satisfy request range.'),
        417: ('Expectation Failed',
              'Expect condition could not be satisfied.'),

        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented',
              'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service Unavailable',
              'The server cannot process the request due to a high load'),
        504: ('Gateway Timeout',
              'The gateway server did not receive a timely response'),
        505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
    }

    # 写入错误
    def write_error(self, code, msg=None):
        s_msg, l_msg = self.responses[code]
        if msg:
            s_msg = msg

        # 错误的html信息
        response_content = self.DEFAULT_ERROR_MESSAGE_TEMPLATE % {
            'code': code,
            'message': s_msg,
            'explain': l_msg
        }
        self.write_response(code, msg)
        # 应答头与应答内容之间有个空行
        self.end_response_headers()
        self.write_content(response_content)

    # 结束应答头
    def end_response_headers(self):
        self.write_content('\r\n')