import socket
import getch
import struct
import time
from threading import Thread
from config import *

while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("0.0.0.0", port))
    print(Bold, "Client started, listening for offer requests...", RESET)
    data, addr = client.recvfrom(1024)
    if not (data[:4] == bytes([0xfe, 0xed, 0xbe, 0xef])) or not (data[4] == 0x02):
        print("Invalid format.")
        continue
    host_ip = addr[0]
    port_host = struct.unpack('>H', data[5:7])[0]
    print(Green, "Received offer from {}, attempting to connect...".format(host_ip), RESET)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port_host))
        s.send('{0}\n'.format('Rak Bibi!').encode())
        start_game = s.recv(1024).decode()
        print(Magenta, start_game, Red, ':')  # Game Start
        game_mode = True

        def game_play():
            while game_mode:
                try:
                    key = getch.getche()
                    s.sendall(str(key).encode('ascii'))
                except: break
                
        game = Thread(target=game_play())
        game.start()
        endgame = s.recv(1024).decode()
        game_mode = False
        game.join()
        print(Yellow, '\n', endgame, RESET)
        time.sleep(3)
