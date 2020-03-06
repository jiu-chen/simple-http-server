# -*- encoding=utf-8 -*-


class BaseRequestHandler:
    def __init__(self, server, request, client_address):
        self.server = server
        self.request = request
        self.client_address = client_address

    # 留给具体的子类去实现
    def handle(self):
        pass


class StreamRequestHandler(BaseRequestHandler):  # 继承
    def __init__(self, server, request, client_address):
        BaseRequestHandler.__init__(self, server, request, client_address)

        # 为了方便，将request分离为读和写的两个文件描述符
        self.rfd = self.request.makefile('rb')
        self.wfd = self.request.makefile('wb')

        self.wbuf = []  # 定义缓存

    # 编码，字符串->字节码
    def encode(self, msg):
        if not isinstance(msg, bytes):
            msg = bytes(msg, encoding='utf-8')
        return msg

    # 解码 字节码 -> 字符串
    def decode(self, msg):
        if isinstance(msg, bytes):  # 如果是字节码
            msg = msg.decode()
        return msg

    # 读消息
    def read(self, length):
        msg = self.rfd.read(length)
        return self.decode(msg)

    # 读取一行消息
    def readline(self, length=65536):  # 如果length没有指定，则length为65536
        msg = self.rfd.readline(length).strip()
        return self.decode(msg)

    # 写消息，写入缓存
    def write_content(self, msg):
        msg = self.encode(msg)  # 将字符串编码为字节码
        self.wbuf.append(msg)

    # 发送消息
    def send(self):
        for line in self.wbuf:
            self.wfd.write(line)
        self.wfd.flush()
        self.wbuf = []

    def close(self):
        self.wfd.close()
        self.rfd.close()
