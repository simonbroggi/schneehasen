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
# see http://pi4j.com/images/j8header.png
# all the green ones except the last (number 29, it's used for input)

DEFAULT_CLIENT_OUTPUT_MAPPINGS = [
    7, 0, 1, 2, 3, 4, 5, 6, 21, 22, 26, 23, 24, 27, 25, 28
]

# default inputs used on clients (for infrared sensors) - on the master,
# these will be seen as inputs 0..n
DEFAULT_CLIENT_INPUT_MAPPINGS = [
    29
]

clientInputMappings = DEFAULT_CLIENT_INPUT_MAPPINGS
clientOutputMappings = DEFAULT_CLIENT_OUTPUT_MAPPINGS


#
# master configuration
#
MASTER_IP = '10.0.0.1'
MASTER_PORT = 12345
