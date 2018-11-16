import ssl
import socket

import server.http


class Handler(ssl.SSLSocket, server.http.Handler):

    certfile = '/etc/letsencrypt/live/desktop.as204416.net/fullchain.pem'
    keyfile = '/etc/letsencrypt/live/desktop.as204416.net/privkey.pem'

    def __init__(self, hostname: str = None, port: int = None, fd: int = None):
        http.Handler.__init__(self, hostname, port, fd)

        context = ssl.SSLContext()
        self._sslobj = context._wrap_socket(self, self.server_side)


class Server(server.http.Server):

    def __init__(self, hostname: str="0.0.0.0", port: int=443, handler=Handler):
        super().__init__(hostname, port, handler)
