CLEAR_SCREEN_BUFFER = b'\xf5\xc3\x11\x5d\x7f\x1d\xc0\x11\x40\x40\x13\xff\xef'

# Telnet protocol commands as bytes
SE = b'\xf0'  # 240, End of subnegotiation parameters
SB = b'\xfa'  # 250, Sub-option to follow
WILL = b'\xfb'  # 251
WONT = b'\xfc'  # 252
DO = b'\xfd'  # 253
DONT = b'\xfe'  # 254
IAC = b'\xff'  # 255
SEND = b'\x01'  # sub-process negotiation SEND
IS = b'\x00'  # sub-process negotiation IS

# TN3270 Telnet commands
TN_ASSOCIATE = b'\x00'
TN_CONNECT = b'\x01'
TN_DEVICETYPE = b'\x02'
TN_FUNCTIONS = b'\x03'
TN_IS = b'\x04'
TN_REASON = b'\x05'
TN_REJECT = b'\x06'
TN_REQUEST = b'\x07'
TN_RESPONSES = b'\x02'
TN_SEND = b'\x08'
TN_TN3270 = b'\x28'  # 40
TN_EOR = b'\xef'  # 239, End of record in 3270 mode

# Supported Telnet Options
options = {
    'BINARY': b'\x00',
    'EOR': b'\x19',
    'TTYPE': b'\x18',
    'TN3270': b'\x28',
    'TN3270E': b'\x1c',
}

supported_options = {
    b'\x00': 'BINARY',
    b'\x19': 'EOR',
    b'\x18': 'TTYPE',
    b'\x28': 'TN3270',
    b'\x1c': 'TN3270E',
}

# TN3270 Stream Commands
EAU = b'\x0f'
EW = b'\x05'
EWA = b'\x0d'
RB = b'\x02'
RM = b'\x06'
RMA = b''
W = b'\x01'
WSF = b'\x11'
NOP = b'\x03'
SNS = b'\x04'
SNSID = b'\xe4'

# SNA equivalents
SNA_RMA = b'\x6e'
SNA_EAU = b'\x6f'
SNA_EWA = b'\x7e'
SNA_W = b'\xf1'
SNA_RB = b'\xf2'
SNA_WSF = b'\xf3'
SNA_EW = b'\xf5'
SNA_NOP = b'\x03'
SNA_RM = b'\xf6'

# TN3270 Stream Orders
SF = b'\x1d'
SFE = b'\x29'
SBA = b'\x11'
SA = b'\x28'
MF = b'\x2c'
IC = b'\x13'
PT = b'\x05'
RA = b'\x3c'
EUA = b'\x12'
GE = b'\x08'

# TN3270 Format Control Orders
NUL = b'\x00'
SUB = b'\x3f'
DUP = b'\x1c'
FM = b'\x1e'
FF = b'\x0c'
CR = b'\x0d'
NL = b'\x15'
EM = b'\x19'
EO = b'\xff'  # same as IAC in ASCII?

# TN3270 Attention Identification (AIDS)
NO = b'\x60'
QREPLY = b'\x61'
ENTER = b'\x7d'
PF1 = b'\xf1'
PF2 = b'\xf2'
PF3 = b'\xf3'
PF4 = b'\xf4'
PF5 = b'\xf5'
PF6 = b'\xf6'
PF7 = b'\xf7'
PF8 = b'\xf8'
PF9 = b'\xf9'
PF10 = b'\x7a'
PF11 = b'\x7b'
PF12 = b'\x7c'
PF13 = b'\xc1'
PF14 = b'\xc2'
PF15 = b'\xc3'
PF16 = b'\xc4'
PF17 = b'\xc5'
PF18 = b'\xc6'
PF19 = b'\xc7'
PF20 = b'\xc8'
PF21 = b'\xc9'
PF22 = b'\x4a'
PF23 = b'\x4b'
PF24 = b'\x4c'
OICR = b'\xe6'
MSR_MHS = b'\xe7'
SELECT = b'\x7e'
PA1 = b'\x6c'
PA2 = b'\x6e'
PA3 = b'\x6b'
CLEAR = b'\x6d'
SYSREQ = b'\xf0'

AIDS = {
    ENTER,
    PF1,
    PF2,
    PF3,
    PF4,
    PF5,
    PF6,
    PF7,
    PF8,
    PF9,
    PF10,
    PF11,
    PF12,
    PF13,
    PF14,
    PF15,
    PF16,
    PF17,
    PF18,
    PF19,
    PF20,
    PF21,
    PF22,
    PF23,
    PF24,
    PA1,
    PA2,
    PA3,
    CLEAR,
}

# For Structured Fields
AID_SF = b'\x88'
SFID_QREPLY = b'\x81'

# Code table for addresses
code_table = [
    0x40,
    0xC1,
    0xC2,
    0xC3,
    0xC4,
    0xC5,
    0xC6,
    0xC7,
    0xC8,
    0xC9,
    0x4A,
    0x4B,
    0x4C,
    0x4D,
    0x4E,
    0x4F,
    0x50,
    0xD1,
    0xD2,
    0xD3,
    0xD4,
    0xD5,
    0xD6,
    0xD7,
    0xD8,
    0xD9,
    0x5A,
    0x5B,
    0x5C,
    0x5D,
    0x5E,
    0x5F,
    0x60,
    0x61,
    0xE2,
    0xE3,
    0xE4,
    0xE5,
    0xE6,
    0xE7,
    0xE8,
    0xE9,
    0x6A,
    0x6B,
    0x6C,
    0x6D,
    0x6E,
    0x6F,
    0xF0,
    0xF1,
    0xF2,
    0xF3,
    0xF4,
    0xF5,
    0xF6,
    0xF7,
    0xF8,
    0xF9,
    0x7A,
    0x7B,
    0x7C,
    0x7D,
    0x7E,
    0x7F,
]

# TN3270 data stream flags
NO_OUTPUT = 0
OUTPUT = 1
BAD_COMMAND = 2
BAD_ADDRESS = 3
NO_AID = 0x60

# 3270E
NO_RESPONSE = 0x00
ERROR_RESPONSE = 0x01
ALWAYS_RESPONSE = 0x02
POSITIVE_RESPONSE = 0x00
NEGATIVE_RESPONSE = 0x01

# 3270E data types
DT_3270_DATA = 0x00
DT_SCS_DATA = 0x01
DT_RESPONSE = 0x02
DT_BIND_IMAGE = 0x03
DT_UNBIND = 0x04
DT_NVT_DATA = 0x05
DT_REQUEST = 0x06
DT_SSCP_LU_DATA = 0x07
DT_PRINT_EOJ = 0x08

NEG_COMMAND_REJECT = 0x00
NEG_INTERVENTION_REQUIRED = 0x01
NEG_OPERATION_CHECK = 0x02
NEG_COMPONENT_DISCONNECTED = 0x03

# Structured Fields
SF_READ_PART = b'\x01'
SF_RP_QUERY = b'\x02'
SF_RP_QLIST = b'\x03'
SF_RPQ_LIST = b'\x00'
SF_RPQ_EQUIV = b'\x40'
SF_RPQ_ALL = b'\x80'
SF_ERASE_RESET = b'\x03'
SF_ER_DEFAULT = b'\x00'
SF_ER_ALT = b'\x80'
SF_SET_REPLY_MODE = b'\x09'
SF_SRM_FIELD = b'\x00'
SF_SRM_XFIELD = b'\x01'
SF_SRM_CHAR = b'\x02'
SF_CREATE_PART = b'\x0c'
CPFLAG_PROT = 0x40
CPFLAG_COPY_PS = 0x20
CPFLAG_BASE = 0x07
SF_OUTBOUND_DS = b'\x40'
SF_TRANSFER_DATA = b'\xd0'

# File Transfer (IND$FILE) constants
TR_OPEN_REQ = 0x0012
TR_CLOSE_REQ = 0x4112
TR_SET_CUR_REQ = 0x4511
TR_GET_REQ = 0x4611
TR_INSERT_REQ = 0x4711
TR_DATA_INSERT = 0x4704

TR_GET_REPLY = 0x4605
TR_NORMAL_REPLY = 0x4705
TR_ERROR_REPLY = 0x08
TR_CLOSE_REPLY = 0x4109

TR_RECNUM_HDR = 0x6306
TR_ERROR_HDR = 0x6904
TR_NOT_COMPRESSED = 0xC080
TR_BEGIN_DATA = 0x61

TR_ERR_EOF = 0x2200
TR_ERR_CMDFAIL = 0x0100

DFT_BUF = 4096
DFT_MIN_BUF = 256
DFT_MAX_BUF = 32768

FT_NONE = 1
FT_AWAIT_ACK = 2

# 3270E negotiation
TN3270E_ASSOCIATE = b'\x00'
TN3270E_CONNECT = b'\x01'
TN3270E_DEVICE_TYPE = b'\x02'
TN3270E_FUNCTIONS = b'\x03'
TN3270E_IS = b'\x04'
TN3270E_REASON = b'\x05'
TN3270E_REJECT = b'\x06'
TN3270E_REQUEST = b'\x07'
TN3270E_SEND = b'\x08'

NEGOTIATING = 0
CONNECTED = 1
TN3270_DATA = 2
TN3270E_DATA = 3

DEVICE_TYPE = 'IBM-3279-2-E'
COLS = 80
ROWS = 24
WORD_STATE = ['Negotiating', 'Connected', 'TN3270 mode', 'TN3270E mode']
TELNET_PORT = 23

telnet_commands = {
    SE: 'SE',
    SB: 'SB',
    WILL: 'WILL',
    WONT: 'WONT',
    DO: 'DO',
    DONT: 'DONT',
    IAC: 'IAC',
    SEND: 'SEND',
    IS: 'IS',
}

telnet_options = {
    TN_ASSOCIATE: 'ASSOCIATE',
    TN_CONNECT: 'CONNECT',
    TN_DEVICETYPE: 'DEVICE_TYPE',
    TN_FUNCTIONS: 'FUNCTIONS',
    TN_IS: 'IS',
    TN_REASON: 'REASON',
    TN_REJECT: 'REJECT',
    TN_REQUEST: 'REQUEST',
    TN_RESPONSES: 'RESPONSES',
    TN_SEND: 'SEND',
    TN_TN3270: 'TN3270',
    TN_EOR: 'EOR',
}

tn3270_options = {
    TN3270E_ASSOCIATE: 'TN3270E_ASSOCIATE',
    TN3270E_CONNECT: 'TN3270E_CONNECT',
    TN3270E_DEVICE_TYPE: 'TN3270E_DEVICE_TYPE',
    TN3270E_FUNCTIONS: 'TN3270E_FUNCTIONS',
    TN3270E_IS: 'TN3270E_IS',
    TN3270E_REASON: 'TN3270E_REASON',
    TN3270E_REJECT: 'TN3270E_REJECT',
    TN3270E_REQUEST: 'TN3270E_REQUEST',
    TN3270E_SEND: 'TN3270E_SEND',
}
