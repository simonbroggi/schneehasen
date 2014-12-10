#!/usr/bin/python
from weakref import WeakKeyDictionary
import time
import sys
import os

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

from actions.base import Action
from actions.states import PrintStateAction
from actions.simple import SingleSnowHare
from actions.multipath import MultipathBase
from actions.multipath import IdleAnimation


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
        print "received input from client ", data
        self._server.update_input(self, data)

    def Close(self):
        self._server.remove_client(self)


class WhiteRabbitServer(Server):
    channelClass = RabbitHole
    exitSignal = False

    inputs = {}
    outputs = {}
    actions = {}
    virtual_inputs = []
    virtual_outputs = []
    framerate = 20
    last_time = 0
    current_time = 0
    delta_time = 0

    def __init__(self, *args, **kwargs):
        self.id = conf.CLIENT_ID
        self.conf = kwargs['conf']
        del kwargs['conf']
        print 'master.conf',self.conf

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

        for output in self.virtual_outputs:
            print output

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
        if index >= len(self.virtual_outputs):
            # na
            print "output "+str(index)+" not available"
            return

        output_info = self.virtual_outputs[index]
        output_info['val'] = val
        client = output_info['client'][0]

        # ask client to set the value on the mapped index
        client.Send({
            'action': 'setoutput',
            'index': output_info['localIndex'],
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

    def update_input(self, client, data):
        print 'server update input', client, data
        local_index = int(data['channel'])
        val = data['val']
        print 'local_index', local_index, 'val', val

        # map local input to virtualized inputs
        for i,_ in enumerate(self.virtual_inputs):
            print(_['client'][0], _['localIndex'])

        matches = [i for i,_ in enumerate(self.virtual_inputs)
                 if (_['client'][0] == client and _['localIndex'] == local_index)]

        if len(matches) > 0:
            print 'setting input ', self.virtual_inputs[matches[0]], ' to val=', val
            self.virtual_inputs[matches[0]]['val'] = val

    def remove_client(self, channel):
        print 'removing client', channel
        del self.clients[channel]
        self.map_clients()

    def launch(self, stdscr=None, *args, **kwds):
        print "White Rabbit Master ready"
        while not self.exitSignal:
            self.current_time = time.time()
            self.delta_time = self.current_time - self.last_time
            if self.delta_time >= (1.0/self.framerate):
                self.run_actions()
                self.last_time = self.current_time

            self.Pump()

            # sleep smallest interval possible on system (~1-10ms)
            time.sleep(0.0001)

    def run_actions(self):
        ordered_actions = sorted(self.actions.items(), key=lambda x: x[1]['weight'])

        for action in ordered_actions:
            action[0].update(self.current_time, self.delta_time)

    def register_action(self, action, weight):
        if not isinstance(action, Action):
            raise BaseException("action doesn't have base type Action", action)

        self.actions[action] = {
            'weight': weight
        }
        action.registered({'master': self, 'framerate': self.framerate})

    def remove_action(self, action):
        del self.actions[action]


# read configuration (optionally from different script)
config_file = 'conf'
if len(sys.argv) == 2:
    config_file = os.path.basename(sys.argv[1])
    if config_file[-3:] == ".py":
        config_file = config_file[:-3]

conf = __import__(config_file, globals(), locals(), [])
print "Using configuration: ", conf



print "White Rabbit Master initializing"
server = WhiteRabbitServer(localaddr=(conf.MASTER_IP, conf.MASTER_PORT), conf=conf)

# add actions
server.register_action(PrintStateAction(), 999)
#server.register_action(SingleSnowHare(), 0)
server.register_action(MultipathBase(config='multipath-left.csv', use_inputs=[0]), 0)
server.register_action(MultipathBase('multipath-right.csv', use_inputs=[1]), 1)
#server.register_action(IdleAnimation('multipath-idle.csv', use_inputs=[0,1]), 2)

# TODO: consolidate outputs (how?)

server.launch()

