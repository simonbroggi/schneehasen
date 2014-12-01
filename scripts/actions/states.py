import sys
from base import Action


class PrintStateAction(Action):
    """
    Periodically print out information on the state of the master.
    """
    def __init__(self):
        Action.__init__(self)
        self.count = 0

    def update(self, current_time, delta_time):
        Action.update(self, current_time, delta_time)
        self.count += 1
        if self.count == 10:
            self.count = 0

            # print out state of master
            self.print_state()


    def get_output_state_string(self):
        """
        builds a readable string of the current output state as seen by the master
        :return: state as nicely formatted string
        """
        if self.master is None:
            return None

        state = ""
        for out in self.master.virtual_outputs:
            if out['val'] > 0:
                # append magic sign - will probably only work on unicode console ;-)
                state += '[' + u"\U0001F407" + ']'
            else:
                state += "[ ]"

        return state

    # prints the state of the master to stdout
    def print_state(self):
        """
        print out state to console
        """
        s = self.get_output_state_string()
        if s is not None:
            sys.stdout.write(s+"\r")
            sys.stdout.flush()

