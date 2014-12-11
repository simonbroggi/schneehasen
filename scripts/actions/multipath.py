from base import Action
import csv
import random
import time

class MultipathBase(Action):
    """
    Complex multi-hare, multi-path simulation where hares can be created either by
    stimulating input or by absence of input.
    """
    def __init__(self, config='multipath-config.csv', use_inputs=[0, 1]):
        Action.__init__(self)

        # read path configuration
        self.matrix = MultipathBase.read_config(config)

        self.hares = []
        self.shadow_inputs = None
        self.timer = self.framerate
        self.DEBUG = False
        self.moves = []
        self.remove_hares = []
        self.use_inputs = use_inputs
        self.input_activation_delay = 0
        self.input_activation_timer = 0

        if self.DEBUG:
            print self.matrix

    def registered(self, options):
        Action.registered(self, options)
        self.input_activation_delay = self.get_activation_delay()
        print 'registered input activation delay in s', self.input_activation_delay

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

    def event_input_changed(self, num, val):
        """
        Event callback when a virtual input changes.
        :param num:
        :param val:
        :return:
        """
        print time.time(), 'event_input_changed', num, val
        if num in set(self.use_inputs) and val > 0:
            speed_factor = random.random()
            # temp for safer debugging
            speed_factor = self.master.conf.DEFAULT_SPEED_FACTOR # 1.5
            hare = ('START', self.timer * speed_factor, speed_factor)
            self.hares += [hare]

            # set new hare
            #self.prepare_move_hare(-1, hare[0])
            print self.hares

    def get_activation_delay(self):
        val = random.randrange(self.master.conf.INPUT_ACTIVATION_DELAY[0], self.master.conf.INPUT_ACTIVATION_DELAY[1]) * self.framerate
        print 'new activation delay:', val
        return val

    def update(self, current_time, delta_time):
        # only run update if there are have outputs
        if len(self.master.virtual_outputs) == 0:
            return

        # only check inputs if configuration is up-to-date
        if len(self.master.virtual_inputs) == len(self.shadow_inputs):
            for i, v in enumerate(self.master.virtual_inputs):
                if self.shadow_inputs[i]['val'] != v['val']:
                    self.event_input_changed(i, v['val'])
                    self.shadow_inputs[i] = v.copy()
                    self.input_activation_timer = self.get_activation_delay()
                elif self.input_activation_delay > 0:
                    """
                    input didn't change and activation delay is set
                    """
                    if (i in set(self.use_inputs)) and (self.input_activation_timer <= 0):
                        print self.input_activation_timer
                        self.event_input_changed(i, v['val'])

            # reset timer after all inputs have been notified
            if (self.input_activation_delay > 0) and (self.input_activation_timer <= 0):
                self.input_activation_timer = self.get_activation_delay()
        else:
            # reconfigure shadow_inputs array
            self.shadow_inputs = [{'val': None}] * len(self.master.virtual_inputs)

        if self.input_activation_delay > 0:
            self.input_activation_timer -= 1

        # move each hare
        if self.DEBUG:
            print self.hares

        for i, val in enumerate(self.hares):
            self.calculate_step(i, current_time)

        self.execute_moves()

        # remove hares
        for i in self.remove_hares:
            print "removing hare ", self.hares[i]
            del self.hares[i]

        self.remove_hares = []

    def calculate_step(self, hare_num, current_time):
        (pos, count, speed_factor) = self.hares[hare_num]
        if self.DEBUG:
            print 'move hare ', hare_num, 'currently at ', pos, 'timer', count
        if count > 0 and type(pos) is int:
            # decrease time counter for this hare
            self.hares[hare_num] = (pos, count - 1, speed_factor)
        else:
            # calculate probable move (no move=stay)
            rnd = random.uniform(0, 1)
            prob_sum = 0.0
            decision = pos
            if self.DEBUG:
                print self.matrix[str(pos)], 'pos', pos
            for target, p in self.matrix[str(pos)]:
                if self.DEBUG:
                    print 'p', p, 'target', target, 'rsum', prob_sum, 'rnd', rnd
                # there are two ways of removing a hare, either go to step 'OFF'
                # or set probability to OFF
                if str(p).upper() == 'OFF':
                    decision = -1
                    # remove hare
                    self.remove_hares += [hare_num]
                else:
                    if rnd < float(p) + prob_sum:
                        decision = target
                        if self.DEBUG:
                            print 'decided to move to ', decision
                        break
                    prob_sum += float(p)

            # move hare
            if pos != decision:
                if self.DEBUG:
                    print 'move from', pos, decision
                if decision.upper() == 'OFF':
                    decision = -1
                    self.remove_hares += [hare_num]

                decision = self.prepare_move_hare(pos, int(decision))

            # save decision, reset timer
            self.hares[hare_num] = (int(decision), self.timer * speed_factor, speed_factor)

    def prepare_move_hare(self, last_position, pos):
        print 'prepare_move_hare',last_position, pos
        if type(last_position) is str and last_position.lower() == 'start':
            last_position = -1

        last_position = int(last_position)
        pos = int(pos)

        # wrap-around if less outputs
        npos = pos
        if pos >= len(self.master.virtual_outputs):
            if self.DEBUG:
                print 'pos truncated to', pos % len(self.master.virtual_outputs)
            npos %= len(self.master.virtual_outputs)

        if last_position >= len(self.master.virtual_outputs):
            print 'last_pos truncated to', last_position % len(self.master.virtual_outputs)
            last_position %= len(self.master.virtual_outputs)

        self.moves += [(last_position, npos)]
        return pos

    def execute_moves(self):
        """
        Consolidates moves (a hare might move to a position that was just left) and send outputs.
        :return:
        """
        positions_old = []
        positions_new = []
        for m in self.moves:
            if m[0] != -1:
                positions_old += [m[0]]
            if m[1] != -1:
                positions_new += [m[1]]

        for i in set(positions_old) - set(positions_new):
            self.set_output(i, 0)

        for i in positions_new:
            if i >= 0:
                self.set_output(i, 1)

        self.moves = []


class IdleAnimation(MultipathBase):
    def __init__(self, config='multipath-idle.csv', use_inputs=[]):
        MultipathBase.__init__(self, config, use_inputs)
        self.idleEvaluationTime = self.framerate # every 1s
        self.idleTimer = self.idleEvaluationTime
        self.prob = 0.1

    def event_input_changed(self, num, val):
        pass

    def registered(self, options):
        MultipathBase.registered(self, options)
        self.idleEvaluationTime = self.master.conf.IDLE_EVALUATION_DELAY * self.framerate

    def update(self, current_time, delta_time):
        MultipathBase.update(self, current_time, delta_time)

        if len(self.master.virtual_outputs) == 0:
            return

        self.idleTimer -= 1
        if self.idleTimer <= 0:
            # idle timer is up - check inputs used
            has_input = False
            for i in self.use_inputs:
                if self.master.virtual_inputs[i]['val'] > 0:
                    has_input = True

            if has_input:
                print "IDLE: timer up but has input - not triggering hare -----"

            trigger = random.random() <= self.master.conf.IDLE_PROBABILITY
            if (not has_input) and trigger and (len(self.hares) < self.master.conf.IDLE_LIMIT):
                print "--> IDLE: launch a rabbit"
                speed_factor = random.uniform(0.01, 3.0)
                self.hares += [('START', self.timer, speed_factor)]
                print self.hares

            self.idleTimer = self.idleEvaluationTime


