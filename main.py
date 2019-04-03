import base64
from synergistic import poller, server, broker


class Handler(server.http.Handler):

    def handle_message(self, message):
        message = message.decode('utf-8')
        method, endpoint, headers, body = self.parse(message)
        host = headers.get('Host', '')
        data = {'host': host, 'method': method, 'endpoint': endpoint, 'headers': headers, 'body': body}
        reverse = '.'.join(host.split('.')[::-1])
        self.broker.publish('request.' + reverse, data, self.callback)

    def callback(self, channel, msg_id, payload):
        encoded = payload.get('b64d', False)
        body = payload.get('body', '')
        if encoded:
            body = base64.b64decode(body)
        self.respond(payload.get('code', 200), body, payload.get('headers', None))
        self.close()


if __name__ == "__main__":
    poller = poller.Poll(catch_errors=False)

    broker_client = broker.Client("127.0.0.1", 8891, broker.Type.SERVER)

    http_server = server.http.Server(hostname="0.0.0.0", handler=Handler)

    Handler.broker = broker_client
    poller.add_client(broker_client)

    poller.add_server(http_server)

    poller.serve_forever()
