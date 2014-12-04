import time
#from ..WhiteRabbitMaster import WhiteRabbitServer

class Action(object):
    """
    Base class to execute actions (similar to Unity's GameObject)
    """
    def __init__(self):
        self.options = {}
        self.framerate = 10

        self.master = None
        """:type : WhiteRabbitServer"""
        self.shadow_inputs = None

    def registered(self, options):
        self.options = options

        # shortcuts
        self.framerate = options['framerate']
        self.master = options['master']
        self.shadow_inputs = self.master.virtual_inputs[:]

    def set_output(self, index, val):
        self.master.set_virtual_out(index, val)

    def update(self, current_time, delta_time):
        pass

