import ssl

from synergistic.server import http


class Handler(ssl.SSLSocket, http.Handler):

    def __init__(self, hostname: str = None, port: int = None, fd: int = None):
        http.Handler.__init__(self, hostname, port, fd)

        context = ssl.SSLContext()
        self._sslobj = context._wrap_socket(self, self.server_side)


class Server(http.Server):

    def __init__(self, hostname: str = "0.0.0.0", port: int = 443, handler=Handler, certfile='', keyfile=''):
        handler.certfile = certfile
        handler.keyfile = keyfile
        super().__init__(hostname, port, handler)
