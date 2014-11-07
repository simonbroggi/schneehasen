#!/usr/bin/python
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep
from weakref import WeakKeyDictionary

"""
LENZERHEIDE ZAUBERWALD 2014 * SCHNEEHASEN

The white rabbit master is the main controller for the snow rabbit installation.
All clients connect to this master and send their inputs. The master decides upon
the action to take.
"""
class RabbitHole(Channel):
    """
    A rabbit hole is the channel for one connected client pi.
    """
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

    def Network_input(self, data):
        print "rabbit client: input changed: ", data

    def Network_carrot(self, data):
        print "rabbit got carrot", data

class WhiteRabbitServer(Server):
    channelClass = RabbitHole
    exitSignal = False

    def __init__(self, *args, **kwargs):
        self.id = 0
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        print 'Server launched'

    def Connected(self, channel, addr):
        print 'new rabbit connection: ', channel

    def Launch(self):
        while not self.exitSignal:
            self.Pump()
            sleep(0.0001)


print "White Rabbit Master initializing"
#localaddr=(host, int(port))
server = WhiteRabbitServer(localaddr=('127.0.0.1', 12345))
server.Launch()
print "White Rabbit Master ready"

