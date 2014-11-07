#!/usr/bin/python
from PodSixNet.Connection import connection, ConnectionListener
from time import sleep
import conf
import consts


__exitSignal__ = False


# generic network listener, used for reconnecting
class WhiteRabbitClient(ConnectionListener):
    host = ''
    port = 0
    state = consts.STATE_DISCONNECTED
    isConnecting = 0
    count = 0

    global __exitSignal__

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connect()

    def Network(self, data):
        print 'network data:', data

    def Network_connected(self, data):
        print "connected to the server"
        self.state = consts.STATE_CONNECTED
        self.isConnecting = 0

    def Network_disconnected(self, data):
        print "disconnected from the server"
        self.state = consts.STATE_DISCONNECTED
        self.isConnecting = 0

    def Network_error(self, data):
        print "error:", data['error'][1]
        self.state = consts.STATE_DISCONNECTED
        self.isConnecting = 0

    def Network_myaction(data):
        print "myaction:", data

    def Network_setoutput(data):
        # set rpi output as the white master wishes
        print data['outputs']

    def connect(self):
        print "Connecting to "+''.join((self.host, ':'+str(self.port)))
        self.isConnecting = 1
        self.Connect((self.host, self.port))

    def reconnect(self):
        # if we get disconnected, only try once per second to re-connect
        print "no connection or connection lost - trying reconnection in 1s..."
        sleep(1)
        self.connect()

    def Loop(self):
        self.Pump()
        connection.Pump()

        # test notify master of carrot found
        if self.count == 1000:
            self.Send({"action": "carrot", "size": "large"})
            self.count = 0
        self.count = self.count + 1

        if self.state == consts.STATE_DISCONNECTED and not self.isConnecting:
            self.reconnect()

#connection.Send({"action": "ping", "blah": 123, "things": [3, 4, 3, 4, 7]})
print "Initial connect..."
client = WhiteRabbitClient('127.0.0.1', 12345)

while not __exitSignal__:
    client.Loop()
    sleep(0.001)
