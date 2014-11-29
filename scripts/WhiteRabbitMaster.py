#!/usr/bin/python
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep
from weakref import WeakKeyDictionary
import sys
import os

# use RPi.GPIO if available, otherwise fallback to FakeRPi.GPIO for testing
try:
    import RPi.GPIO as io
except ImportError:
    import FakeRPi.GPIO as io


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

    def Network_config(self, data):
        print "received client config", data
        # insert and map client inputs/outputs
        self._server.update_clients(self, data)

    def Network_carrot(self, data):
        print "rabbit got carrot", data

    def Network_input(self, data):
        print "received input from client "+data
        self._server.update_input(self, data)

    def Close(self):
        self._server.remove_client(self)


class WhiteRabbitServer(Server):
    channelClass = RabbitHole
    exitSignal = False

    inputs = {}
    outputs = {}

    def __init__(self, *args, **kwargs):
        self.id = conf.CLIENT_ID
        self.virtual_outputs = []
        Server.__init__(self, *args, **kwargs)

        self.clients = WeakKeyDictionary()
        print 'Server launched'

    def Connected(self, channel, addr):
        print 'new rabbit hole: ', channel

    def update_clients(self, channel, data):
        print 'updating client information on server:', channel, data

        # store client data
        self.clients[channel] = {
            'numInputs': data['inputs'],
            'numOutputs': data['outputs'],
            'outputWeight': data['outputWeight'],
            'inputWeight': data['inputWeight']
        }

        # update virtual input and output mappings
        self.map_clients()

    def map_clients(self):
        # generate virtual map of all available outputs
        print self.clients.items()
        for item in self.clients.items():
            print item

        ordered_clients = sorted(self.clients.items(), key=lambda x: x[1]['outputWeight'])
        self.virtual_outputs = []
        for client in ordered_clients:
            for i in range(client[1]['numOutputs']):
                self.virtual_outputs = self.virtual_outputs + [{
                    'client': client,
                    'localIndex': i,
                    'val': None
                }]

        # generate virtual map of all available inputs
        ordered_clients = sorted(self.clients.items(), key=lambda x: x[1]['inputWeight'])
        self.virtual_inputs = []
        for client in ordered_clients:
            for i in range(client[1]['numInputs']):
                self.virtual_inputs = self.virtual_inputs + [{
                    'client': client,
                    'localIndex': i,
                    'val': None
                }]

    # set a new value of an output pin with a virtual index
    # will send value to client
    def set_virtual_out(self, index, val):
        if index > len(self.virtual_outputs):
            # na
            print "output "+index+" not available"

        client_info = self.virtual_outputs[index]
        client = client_info['client']

        # ask client to set the value on the mapped index
        client.Send({
            'action': 'setoutput',
            'index': client_info['localIndex'],
            'val': val
        })

        # we don't care about feedback... :-)

    # get the last known value of an input pin with a virtual index
    def get_virtual_in(self, index):
        if index > len(self.virtual_inputs):
            # na
            print "input "+index+" not available"

        client_info = self.virtual_inputs[index]
        return client_info['val']


    def update_input(self, channel, data):
        print 'server update input', data
        index = data['channel']
        val = data['val']

    # builds a readable string of the current output state as seen by the master
    def get_output_state_string(self):
        state = ""
        for out in self.virtual_outputs:
            if out['val'] > 0:
                # append magic sign - will probably only work on unicode console ;-)
                state += '[' + u"\U0001F407" + ']'
            else:
                state += "[ ]"
        return state

    # prints the state of the master to stdout
    def print_state(self):
        s = self.get_output_state_string()
        if s is not None:
            sys.stdout.write(s+"\r")

    def remove_client(self, channel):
        print 'removing client', channel
        del self.clients[channel]
        self.map_clients()
        
    def launch(self):
        timer = 0
        interval = 0.0001
        while not self.exitSignal:
            self.Pump()

            # print state from time to time
            if timer % 100 == 0:
                self.print_state()
                timer = 0

            timer += 1
            sleep(interval)


# read configuration (optionally from different script)
config_file = 'conf'
if len(sys.argv) == 2:
    config_file = os.path.basename(sys.argv[1])
    if config_file[-3:] == ".py":
        config_file = config_file[:-3]

conf = __import__(config_file, globals(), locals(), [])
print "Using configuration: ", conf

print "White Rabbit Master initializing"
#localaddr=(host, int(port))
server = WhiteRabbitServer(localaddr=(conf.MASTER_IP, conf.MASTER_PORT))
server.launch()
print "White Rabbit Master ready"

