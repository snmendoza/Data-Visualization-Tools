

import configuration
# from kivy.clock import Clock
# from multiprocessing.connection import Listener
import rpyc

class DaemonService(rpyc.Service):
    def on_connect(self, conn):
        print(conn, 'connected')

    def on_disconnect(self, conn):
        print(conn, 'disconnect')

    def exposed_print(self, arg):
        print(arg)
