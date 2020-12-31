import scapy.all as s

"""
Provide global configuration variables inside the typical 'config.py'
"""

host = s.get_if_addr('eth1')
host_test = s.get_if_addr('eth2')
port = 13117

game_time = 10
udp_time = 10

Black = '\u001b[30;1m'
Red = '\u001b[31;1m'
Green = '\u001b[32;1m'
Yellow = '\u001b[33;1m'
Blue = '\u001b[34;1m'
Magenta = '\u001b[35;1m'
Cyan = '\u001b[36;1m'
White = '\u001b[37;1m'
Bold = '\u001b[1m'
BgWhite = '\u001b[47;1m'
RESET = '\u001b[0m'
