from base import Action

class SingleSnowHare(Action):
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

        if self.position == -1:
            self.move(self.start_position)

        self.count += 1
        if float(self.count)/self.framerate >= 1:
            self.last_position = self.position
            self.position = (self.position + 1) % len(self.master.virtual_outputs)
            self.move(self.position)
            self.count = 0

    def move(self, pos):
        if self.last_position >= 0:
            self.set_output(self.last_position, 0)

        self.set_output(pos, 1)

