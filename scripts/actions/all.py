from base import Action

class AllSnowHares(Action):
    """
    Let's a single snow hare run step-by-step linearly through all boxes.
    """
    def __init__(self):
        Action.__init__(self)
        self.count = 0
        self.position = -1
        self.last_position = -1
        self.start_position = 0

    def update(self, current_time, delta_time):
        if len(self.master.virtual_outputs) == 0:
            return

        self.count += 1
        if float(self.count)/self.framerate >= 1:

            # for i in range(0, 9)
            for i in range(0, len(self.master.virtual_outputs)):
                self.set_output(i, 1)

            #self.set_output(0, 1)

            self.count = 0
