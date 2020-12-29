import codecs
import struct

import dataclasses as dataclasses

host = '172.1.0.35'
port = 13117
ip_start = host[:host.rfind('.') + 1]

ip_range_list = ['{}{}'.format(ip_start, x) for x in range(0, 256)]

ip_range_list.append('172.1.0.35')


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\u001b[31m'
    Magenta = '\u001b[35'
    Yellow = '\u001b[33'
    purple = '\033[35m'
    RESET = '\u001b[0m'
    BackgroundBrightMagenta = '\u001b[45;1m'
    BackgroundBrightCyan = '\u001b[46;1m'
    pink = '\033[91m'
    B_White = "\x1b[107m"
    darkgrey = '\033[90m'
    white= '\u001b[37m'


