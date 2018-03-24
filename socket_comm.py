from __future__ import unicode_literals
import xlwings as xw

# from kivy.uix.widget import Widget
# from kivy.support import install_twisted_reactor
#
# install_twisted_reactor()

# A Simple Client that send messages to the Echo Server
from twisted.internet import reactor, protocol

class EchoClient(protocol.Protocol):
    def connectionMade(self):
        self.factory.cls.on_connection(self.transport)

    def dataReceived(self, data):
        self.factory.cls.print_message(data.decode('utf-8'))


class EchoClientFactory(protocol.ClientFactory):
    protocol = EchoClient

    def __init__(self, cls):
        self.cls = cls
        super().__init__()

    def startedConnecting(self, connector):
        self.cls.print_message('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        self.cls.print_message('Lost connection.')

    def clientConnectionFailed(self, connector, reason):
        self.cls.print_message('Connection failed.')


factory = EchoClientFactory()
def plot(filename = None):
    if not filename:
        filename = get_name()
        reactor.connectTCP(host, port, EchoClientFactory())
    cls = TwistedClientApp()
    cls.connect_to_server()
    cls.send_message(filename)

def get_name():
    wb = xw.Book.caller()
    return wb

if __name__ == '__main__':
    cls = TwistedClientApp()
    cls.connect_to_server()
