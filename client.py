import socket
import getch

from config import *
from threading import Thread

while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("0.0.0.0", port))
    print(bcolors.BOLD,"Client started, listening for offer requests..." ,bcolors.RESET)
    data, addr = client.recvfrom(1024) 
    if not (data[:4] == bytes([0xfe, 0xed, 0xbe, 0xef])) or not (data[4] == 0x02):
        print("Invalid format.")
        continue
    host = addr[0]
    port_new = struct.unpack('>H', data[5:7])[0]
    print(bcolors.OKGREEN, "Received offer from {}, attempting to connect...".format(host) ,bcolors.RESET)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port_new))
        s.send('{0}\n'.format('rak bibi').encode())
        startgame = s.recv(1024).decode()
        print(bcolors.purple, startgame ,bcolors.pink,':') # Game Start
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
        print(bcolors.OKBLUE,'\n', endgame ,bcolors.RESET)
        