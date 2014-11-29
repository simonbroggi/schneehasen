#!/usr/bin/python
from PodSixNet.Connection import connection, ConnectionListener
from time import sleep
import consts
import os
import sys
import time

__exitSignal__ = False


# use RPi.GPIO if available, otherwise fallback to FakeRPi.GPIO for testing
try:
    import RPi.GPIO as io
except ImportError:
    import FakeRPi.GPIO as io


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
        self.send_config()

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
        print "no connection or connection lost - trying reconnection in %ds..." % conf.NETWORK_CONNECT_RETRY_DELAY
        sleep(conf.NETWORK_CONNECT_RETRY_DELAY)
        self.connect()

    def send_config(self):
        self.Send({
            'action': 'config',
            'id': conf.CLIENT_ID,
            'inputs': conf.CLIENT_NUM_INPUTS,
            'outputs': conf.CLIENT_NUM_OUTPUTS,
            'inputWeight': conf.CLIENT_WEIGHT_INPUTS,
            'outputWeight': conf.CLIENT_WEIGHT_OUTPUTS
        })

    def event_input(self, channel, val):
        print "input event on channel "+channel+" val="+val+" delegating to master "
        self.Send({
            'action': 'in',
            'id': conf.CLIENT_ID,
            'channel': channel,
            'val': val
        })

    def Loop(self):
        self.Pump()
        connection.Pump()

        # test notify master of carrot found
        if self.count == 1000:
            #self.Send({"action": "carrot", "size": "large"})
            self.count = 0
        self.count += + 1

        if self.state == consts.STATE_DISCONNECTED and not self.isConnecting:
            self.reconnect()



# read configuration (optionally from different script)
config_file = 'conf'
if len(sys.argv) == 2:
    config_file = os.path.basename(sys.argv[1])
    if config_file[-3:] == ".py":
        config_file = config_file[:-3]

print "Reading configuration from file ", config_file
conf = __import__(config_file, globals(), locals(), [])


print "Initializing GPIO"
io.setmode(io.BCM)
for pin in conf.clientInputMappings:
    print "- set pin "+str(pin)+" as INPUT"
    io.setup(pin, io.IN)

for pin in conf.clientOutputMappings:
    print "- set pin "+str(pin)+" as OUTPUT"
    io.setup(pin, io.OUT)


print "Connecting to master"
client = WhiteRabbitClient(conf.RABBIT_MASTER, conf.RABBIT_MASTER_PORT)

# delegate input callback to network client
def event_input_callback(channel):
    client.event_input(channel, io.input(channel))

print "Adding input callbacks"
for pin in conf.clientInputMappings:
    io.add_event_detect(pin, io.BOTH, callback=event_input_callback)

while not __exitSignal__:
    client.Loop()
    sleep(0.001)

io.cleanup()
