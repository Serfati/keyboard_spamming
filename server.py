import random
import selectors
import socket
import struct
import time
import types
from threading import Thread

from config import *

team_map = {'group 1': [], 'group 2': []}
group1_ips = []
group2_ips = []
counter_group1 = 0
counter_group2 = 0
a_dict = {}
counter_group1_total = 0
counter_group2_total = 0
total_games = 0

sel = selectors.DefaultSelector()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lsock:
    lsock.bind((host, port))
    lsock.listen()
    print(Bold, 'Server started, listening on IP address ', host, RESET)
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)


    def accept_wrapper(sock):
        conn, addr = sock.accept()  # Should be ready to read
        print(Green, 'accepted connection from', RESET, addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        sel.register(conn, events, data=data)


    def client_to_team(key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024).decode("utf-8")  # Should be ready to read
            if recv_data:
                if len(team_map.get('group 1')) < len(team_map.get('group 2')):
                    team_map['group 1'].append((recv_data, key, mask))
                    group1_ips.append(data.addr)
                elif len(team_map.get('group 2')) > len(team_map.get('group 1')):
                    team_map['group 2'].append((recv_data, key, mask))
                    group2_ips.append(data.addr)
                else:
                    group, arr = random.choice(list(team_map.items()))
                    team_map[group].append((recv_data, key, mask))
                    if group == 'group 1':
                        group1_ips.append(data.addr)
                    else:
                        group2_ips.append(data.addr)
            else:
                try:
                    sel.unregister(sock)
                    sock.close()
                    print(Magenta + Bold + 'closing connection to', data.addr)
                except:
                    pass


    def send_start_game(key, mask, group1, group2):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            data.outb += """Welcome to Keyboard Spamming Battle Royale.
Group 1:
==
{}
Group 2:
==
{}
Start pressing keys on your keyboard as fast as you can!!""".format(group1, group2).encode('ascii')
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                try:
                    sent = sock.send(data.outb)  # Should be ready to write
                    data.outb = data.outb[sent:]
                except:
                    for conn in team_map.get('group 1'):
                        if conn[1] == key:
                            team_map.get('group 1').remove(conn)
                    for conn in team_map.get('group 2'):
                        if conn[1] == key:
                            team_map.get('group 2').remove(conn)
                    try:
                        sel.unregister(sock)
                        sock.close()
                        print(Magenta + Bold + 'closing connection to', data.addr)
                    except:
                        pass


    def get_char_from_client(key, mask):
        global counter_group1
        global counter_group2
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                if recv_data.decode('ascii') in a_dict:
                    a_dict[recv_data.decode('ascii')] = a_dict[recv_data.decode('ascii')] + 1
                else:
                    a_dict[recv_data.decode('ascii')] = 1
                if data.addr in group1_ips:
                    counter_group1 = counter_group1 + 1
                elif data.addr in group2_ips:
                    counter_group2 = counter_group2 + 1
            else:
                try:
                    sel.unregister(sock)
                    sock.close()
                    print(a_dict)
                    print(Yellow + Bold + 'closing connection to', data.addr)
                except:
                    pass
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]


    def send_game_over(key, mask, msg):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            data.outb += msg
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                try:
                    sent = sock.send(data.outb)  # Should be ready to write
                    data.outb = data.outb[sent:]
                    try:
                        sel.unregister(sock)
                        sock.close()
                        print(Cyan + Bold + 'closing connection to', data.addr)
                    except:
                        pass
                except:
                    try:
                        sel.unregister(sock)
                        sock.close()
                        print(Cyan + Bold + 'closing connection to', data.addr)
                    except:
                        pass


    def send_udp_invaite():
        frame = bytes([0xfe, 0xed, 0xbe, 0xef])
        type = bytes([0x02])
        s = struct.pack('>H', port)
        msg = frame + type + s
        t_end = time.time() + 10
        ip_start = host[:host.rfind('.') + 1]
        ip_range_list = ['{}{}'.format(ip_start, x) for x in range(0, 256)]
        while time.time() < t_end:
            for ip in ip_range_list:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.sendto(msg, (ip, port))
                    sock.close()
                except:
                    pass


    def main():
        global group1_ips, group2_ips, team_map, counter_group1, counter_group2, a_dict, counter_group1_total, counter_group2_total, total_games

        while True:
            total_games += 1
            t1 = Thread(name='udp', target=send_udp_invaite)
            t1.setDaemon(True)
            t1.start()
            t_end = time.time() + 10
            while time.time() < t_end:
                events = sel.select(timeout=(t_end - time.time()))
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        client_to_team(key, mask)
            t1.join()
            print("group1= ", group1_ips)
            print("group2= ", group2_ips)

            group1 = ''.join([i[0] for i in team_map.get('group 1')])
            group2 = ''.join([i[0] for i in team_map.get('group 2')])
            for client in team_map.get('group 1'):
                send_start_game(client[1], client[2], group1, group2)
            for client in team_map.get('group 2'):
                send_start_game(client[1], client[2], group1, group2)

            t_end = time.time() + 10
            while time.time() < t_end:
                events = sel.select(timeout=(t_end - time.time()))
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        get_char_from_client(key, mask)
            if counter_group1 > counter_group2:
                winner_group = "Group 1 wins!"
                winner_group_teams = group1
                counter_group1_total += 1
            elif counter_group1 < counter_group2:
                winner_group = "Group 2 wins!"
                winner_group_teams = group2
                counter_group2_total += 1
            else:
                winner_group = "Draw between Group 1 and Group 2"
                winner_group_teams = group1 + group2
                counter_group1_total += 1
                counter_group2_total += 1
            winner_msg = """Game over!
Group 1 typed in {} characters. Group 2 typed in {} characters.
{} 

Congratulations to the winners:
==
{}""".format(counter_group1, counter_group2, winner_group, winner_group_teams).encode('ascii')

            for client in team_map.get('group 1'):
                send_game_over(client[1], client[2], winner_msg)
            for client in team_map.get('group 2'):
                send_game_over(client[1], client[2], winner_msg)

            team_map = {'group 1': [], 'group 2': []}
            group1_ips = []
            group2_ips = []
            counter_group1 = 0
            counter_group2 = 0
            print(Cyan + "“Game over, sending out offer requests...")


    if __name__ == '__main__':
        main()
