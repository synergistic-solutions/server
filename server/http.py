import time
import json
import typing
import socket


RESPONSE_CODES = {
    100:    "Continue",
    101:    "Switching Protocols",
    102:    "Processing",
    103:    "Early Hints",

    200:    "OK",
    201:    "Created",
    202:    "Accepted",
    203:    "Non-Authoritative Information",
    204:    "No Content",
    205:    "Reset Content",
    206:    "Partial Content",
    207:    "Multi-Status",
    208:    "Already Reported",
    226:    "IM Used",

    300:    "Multiple Choices",
    301:    "Moved Permanently",
    302:    "Found",
    303:    "See Other",
    304:    "Not Modified",
    305:    "Use Proxy",
    306:    "(Unused)",
    307:    "Temporary Redirect",
    308:    "Permanent Redirect",

    400:    "Bad Request",
    401:    "Unauthorized",
    402:    "Payment Required",
    403:    "Forbidden",
    404:    "Not Found",
    405:    "Method Not Allowed",
    406:    "Not Acceptable",
    407:    "Proxy Authentication Required",
    408:    "Request Timeout",
    409:    "Conflict",
    410:    "Gone",
    411:    "Length Required",
    412:    "Precondition Failed",
    413:    "Payload Too Large",
    414:    "URI Too Long",
    415:    "Unsupported Media Type",
    416:    "Range Not Satisfiable",
    417:    "Expectation Failed",
    421:    "Misdirected Request",
    422:    "Unprocessable Entity",
    423:    "Locked",
    424:    "Failed Dependency",
    425:    "Unassigned",
    426:    "Upgrade Required",
    427:    "Unassigned",
    428:    "Precondition Required",
    429:    "Too Many Requests",
    430:    "Unassigned",
    431:    "Request Header Fields Too Large",
    451:    "Unavailable For Legal Reasons",

    500:    "Internal Server Error",
    501:    "Not Implemented",
    502:    "Bad Gateway",
    503:    "Service Unavailable",
    504:    "Gateway Timeout",
    505:    "HTTP Version Not Supported",
    506:    "Variant Also Negotiates",
    507:    "Insufficient Storage",
    508:    "Loop Detected",
    510:    "Not Extended",
    511:    "Network Authentication",
}

CONTENT_TYPES = {
    "bin": "application/octet-stream",
    "bz": "application/x-bzip",
    "bz2": "application/x-bzip2",
    "css": "text/css",
    "csv": "text/csv",
    "gif": "image/gif",
    "htm": "text/html",
    "html": "text/html",
    "ico": "image/x-icon",
    "jpeg": "image/jpeg",
    "ipg": "image/jpeg",
    "js": "application/javascript",
    "json": "application/json",
    "png": "image/png",
    "pdf": "application/pdf",
    "sh": "application/x-sh",
    "tar": "application/x-tar",
    "ttf": "font/ttf",
    "txt": "text/plain",
    "webm": "video/webm",
    "xml": "application/xml",
    "zip": "application/zip",
}


class Handler(socket.socket):
    server_name = 'Python socket server'

    def __init__(self, hostname: str=None, port: int=None, fd: int=None):
        if (not hostname or not port) and fd is None:
            raise AttributeError

        socket.socket.__init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, fileno=fd)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if hostname and port:
            self.connect((hostname, port))

        self.buffer = b''
        self._closed = False

    def on_receive(self):
        message = self.recv(4096)
        if not message:
            self.close()
            return

        self.buffer += message
        if message.endswith(b'\r\n'):
            self.handle_message(self.buffer)
            self.buffer = b''

    def parse(self, message):
        try:
            bulk_headers, body = message.split('\r\n\r\n', 1)
        except ValueError:
            bulk_headers = message
            body = ''
        headers_list = bulk_headers.split('\r\n')
        request = headers_list[0]
        headers = {}

        for header in headers_list[1:]:
            if header:
                key, value = header.split(':', 1)
                headers[key] = value.lstrip()

        method, url, version = (request + '  ').split(' ', 2)
        if headers.get('Content-Type', '') == 'text/html; charset=UTF-8' and body:
            data = {}
            for arg in body.split('&'):
                key, value = arg.split('=')
                data[key] = value.strip()
        elif headers.get('Content-Type', '') == 'application/json':
            data = json.loads(body)
        elif '?' in url:
            data = {}
            url, args = url.split('?', 1)
            for arg in args.split('&'):
                key, value = arg.split('=')
                data[key] = value.strip()
        else:
            data = body
        return method.upper(), url.lower(), headers, data

    def respond(self, code: int = 200, message: typing.Union[str, bytes] = '', headers: dict = None):
        default_headers = {
            'Date': time.strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'Content-Type': 'text/html; charset=UTF-8',
            'Content-Length': str(len(message)),
            'Server': self.server_name,
        }
        # populate the headers with any additional to the defaults if provided
        # could have used .setdefault on the dict object
        if headers:
            default_headers = {**default_headers, **headers}

        response = 'HTTP/1.1 ' + str(code) + ' ' + RESPONSE_CODES[code]
        for key, value in default_headers.items():
            response += '\r\n' + key + ': ' + value

        response = response.encode('utf-8')

        if isinstance(message, str):
            message = message.encode('utf-8')

        response += b'\r\n\r\n' + message + b'\r\n'

        self.send(response)

    def handle_message(self, message):
        message = message.decode('utf-8')
        method, endpoint, headers, body = self.parse(message)
        print(method, endpoint)
        self.respond(message="ok")
        self.close()


class Server(socket.socket):

    def __init__(self, hostname: str="127.0.0.1", port: int=80, handler: typing.Type[socket.socket]=Handler):
        socket.socket.__init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((hostname, port))
        self.listen(5)
        self.handler = handler

    def on_connect(self):
        original_client_conn, address = self.accept()
        client_conn = self.handler(fd=original_client_conn.fileno())
        original_client_conn.detach()
        return client_conn
