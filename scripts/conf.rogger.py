# configuration template to be used in git
# copy to conf.py locally and adjust

#
# global configuration
#


#
# client configuration
#

# networking
NETWORK_CONNECT_RETRY_DELAY = 3

# information about where to send data
RABBIT_MASTER = '10.0.0.1'
RABBIT_MASTER_PORT = 12345


# id for this specific client - must be unique in the network
CLIENT_ID = 'ROGGER'


# clients will be mapped in the master by weight and dynamically
# assign the input/output slots
# the lower, the lower the input mapping will be (e.g. the first
# one maps outputs from (0..CLIENT_NUM_OUTPUTS)
CLIENT_WEIGHT_OUTPUTS = 0
CLIENT_WEIGHT_INPUTS = 0

# default map for available outputs (with virtual numbering 0..numOutputs)
# to Raspberry Pi B+ board mapping (BCM)
#
# http://pi4j.com/images/j8header.png seems to be wrong for B+
# see http://raspberrypi.stackexchange.com/questions/12966/what-is-the-difference-between-board-and-bcm-for-gpio-pin-numbering
# all the green ones except the last (number 21, it's used for input)

DEFAULT_CLIENT_OUTPUT_MAPPINGS = [
    4, 17, 18, 27, 22, 23, 24, 25,  5,  6, 12, 13, 19, 16, 26, 20
]

# default inputs used on clients (for infrared sensors) - on the master,
# these will be seen as inputs 0..n
DEFAULT_CLIENT_INPUT_MAPPINGS = [
    21
]

clientInputMappings = DEFAULT_CLIENT_INPUT_MAPPINGS
clientOutputMappings = DEFAULT_CLIENT_OUTPUT_MAPPINGS


#
# master configuration
#
MASTER_IP = '10.0.0.1'
MASTER_PORT = 12345
