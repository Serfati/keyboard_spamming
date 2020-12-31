import socket
import kbhit
import struct
import time
from config import *

"""
Client main function, runs from the beginning of the Client.
"""
try:
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            client.bind(("0.0.0.0", port))
            print(Bold, "Client started, listening for offer requests...", RESET)
            data, addr = client.recvfrom(RECIEVE_BUFFER_SIZE)

            """
            Validates that the sent data contains the magic_cookie = 0xfeedbeef and m_type = 0x2
            If data is not valid, returns false.
            """
            if not (data[:4] == bytes([0xfe, 0xed, 0xbe, 0xef])) or not (data[4] == 0x02):
                print("Invalid format.")
                continue

            host_ip = addr[0]
            port_host = struct.unpack('>H', data[5:7])[0]
            print(Green, "Received offer from {}, attempting to connect...".format(
                host_ip), RESET)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                client_team_name = 'Rak Bibi!'
                s.connect((host, port_host))
                s.send('{0}\n'.format(client_team_name).encode('utf-8'))
                start_game = s.recv(RECIEVE_BUFFER_SIZE).decode()
                print(Magenta, start_game, Red, ':')  # Game Start
                end_time = time.time() + game_time

                # game mode - any key press event is caught and sent to the server

                def game_play():
                    kb = kbhit.KBHit()
                    while time.time() < end_time:
                        try:
                            if kb.kbhit():
                                kb.__init__()
                                s.send(b'.')
                                print('.', end='')
                        except:
                            break
                game_play()
                endgame = s.recv(RECIEVE_BUFFER_SIZE).decode()
                print(Yellow, '\n', endgame, RESET)
        except ConnectionRefusedError:
            print('Server disconnected')
            continue

        except Exception:
            print('general_exception')
            continue
except KeyboardInterrupt:
    print('bye!')
    pass
