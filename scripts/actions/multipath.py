from base import Action
import csv
import random

class MultipathHares(Action):
    """
    Complex multi-hare, multi-path simulation where hares can be created either by
    stimulating input or by absence of input.
    """
    def __init__(self):
        Action.__init__(self)

        # read path configuration
        self.matrix = MultipathHares.read_config('multipath-config.csv')

        self.hares = []
        self.timer = self.framerate
        self.DEBUG = False

        if self.DEBUG:
            print self.matrix

    @staticmethod
    def read_config(filename):
        """
        Parses adjacency matrix from csv file
        :param filename: csv file containing adjacency matrix
        :return: dict containing matrix
        """
        matrix = {}
        with open(filename, 'rU') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
            for row in reader:
                num = row['FROM']
                matrix[num] = []
                for i in row.keys():
                    if (str(row[i]) > '') and (i != 'FROM'):
                        # with probability row[i] transition to i
                        matrix[num] += [(str(i), str(row[i]))]

                # sort ascending by probability
                matrix[num] = sorted(matrix[num], key=lambda v: v[1])

        # optional todo: normalize probabilities between 0..1
        return matrix


    def update(self, current_time, delta_time):
        if len(self.master.virtual_outputs) == 0:
            return

        # test: start with one hare at position 0 and once per second
        if len(self.hares) == 0:
            self.hares = [(0, self.timer)]

        # move each hare
        if self.DEBUG:
            print self.hares
        for i, val in enumerate(self.hares):
            (pos, count) = val
            if self.DEBUG:
                print 'move hare ', i, 'currently at ', pos, 'timer', count
            if count > 0:
                # decrease time counter for this hare
                self.hares[i] = (pos, count - 1)
            else:
                # calculate probable move (no move=stay)
                rnd = random.uniform(0, 1)
                rsum = 0.0
                decision = pos
                if self.DEBUG:
                    print self.matrix[str(pos)], 'pos', pos
                for target, p in self.matrix[str(pos)]:
                    if self.DEBUG:
                        print 'p', p, 'target', target, 'rsum', rsum, 'rnd', rnd
                    if rnd < float(p)+rsum:
                        decision = target
                        if self.DEBUG:
                            print 'decided to move to ', decision
                        break
                    rsum += float(p)

                # move hare
                if pos != decision:
                    if self.DEBUG:
                        print 'move from', pos, decision
                    decision = self.move(int(pos), int(decision))

                # save decision, reset timer
                self.hares[i] = (int(decision), self.timer)

    def move(self, last_position, pos):
        if last_position >= 0:
            self.set_output(last_position, 0)

        # prevent overflows
        if pos < 0 or pos >= len(self.master.virtual_outputs):
            if self.DEBUG:
                print 'pos truncated to', pos % len(self.master.virtual_outputs)
            pos %= len(self.master.virtual_outputs)

        self.set_output(pos, 1)
        return pos
