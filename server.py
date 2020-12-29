import dataclasses
import random
import selectors
import socket
import struct
import time
import types
from threading import Thread
from config import *
import operator

team_map = {'group 1': [], 'group 2': []}
group1_ips = []
group2_ips = []
group1 = []
group2 = []
couter_group1 = 0
couter_group2 = 0
a_dict= {}
couter_group1_total = 0
couter_group2_total = 0
total_games = 0
most_commun_char = {}

sel = selectors.DefaultSelector()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lsock:
    lsock.bind((host, port))
    lsock.listen()
    print(Bold, 'Server started, listening on IP address ', host, RESET)
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)


    def accept_wrapper(sock):
        conn, address = sock.accept()  # Should be ready to read
        print(Green, 'accepted connection from', RESET, address)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=address, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        sel.register(conn, events, data=data)

    def send_udp_broadcast():
        frame = [0xfe, 0xed, 0xbe, 0xef]
        type = [0x02]
        s = struct.pack('>H', port)
        msg = bytes(frame) + bytes(type) + bytes(s)
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

    def create_team(key, mask, recv_data):
        if len(team_map.get('group 1')) == len(team_map.get('group 2')):
            group, arr = random.choice(list(team_map.items()))
            team_map[group].append((recv_data, key, mask))
            if group == 'group 1':
                group1_ips.append(key.data.addr)
                group1.append(arr[0][0][:-1])
            else:
                group2_ips.append(key.data.addr)
                group2.append(arr[0][0][:-1])
        elif (len(team_map.get('group 1')) < len(team_map.get('group 2'))):
            team_map['group 1'].append((recv_data, key, mask))
            group1_ips.append(key.data.addr)
            group1.append(recv_data)
        elif (len(team_map.get('group 2')) < len(team_map.get('group 1'))):
            team_map['group 2'].append((recv_data, key, mask))
            group2_ips.append(key.data.addr)
            group2.append(recv_data)

    def get_char_from_client(sock, data, mask):
        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(1024)  # Should be ready to read
                if recv_data:
                    update_dict(recv_data, data)
                else:
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

    def update_dict(recv_data, data):
        if recv_data.decode('ascii') in a_dict:
            a_dict[recv_data.decode('ascii')] = a_dict[recv_data.decode('ascii')] + 1
        else:
            a_dict[recv_data.decode('ascii')] = 1
        if (data.addr in group1_ips):
            global couter_group1
            couter_group1 = couter_group1 + 1
        elif (data.addr in group2_ips):
            global couter_group2
            couter_group2 = couter_group2 + 1

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
                    sel.unregister(sock)
                    sock.close()
                    print(Cyan + Bold + 'closing connection to', data.addr)
                except:
                    pass

    def display_team():
        for client in team_map.get('group 1'):
            sock = client[1].fileobj
            data = client[1].data
            sent_client_start_msg(sock, data, client[1], client[2])
        for client in team_map.get('group 2'):
            sock = client[1].fileobj
            data = client[1].data
            sent_client_start_msg(sock, data, client[1], client[2])

    def sent_client_start_msg(sock, data, key, mask):
        if mask & selectors.EVENT_READ:
            group1_name = ''.join([i[0] for i in team_map.get('group 1')])
            group2_name = ''.join([i[0] for i in team_map.get('group 2')])
            start_msg = f"Welcome to Keyboard Spamming Battle Royale.\n Group 1:\n ==\n {group1_name}\n Group 2:\n ==\n {group2_name}\n Start pressing keys on your keyboard as fast as you can!!"
            data.outb += start_msg.encode('ascii')
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                try:
                    sent = sock.send(data.outb)  # Should be ready to write
                    data.outb = data.outb[sent:]
                except:
                    delete_team(sock, data, key)

    def delete_team(sock, data, key):
        try:
            for conn in team_map.get('group 1'):
                if conn[1] == key:
                    team_map.get('group 1').remove(conn)
            for conn in team_map.get('group 2'):
                if conn[1] == key:
                    team_map.get('group 2').remove(conn)
            sel.unregister(sock)
            sock.close()
            print(Magenta + Bold + 'closing connection to', data.addr)
        except:
            pass

    def display_game_result():
        global couter_group1, couter_group2, couter_group1_total, couter_group2_total, a_dict
        if (couter_group1 > couter_group2):
            winner_group = "Group 1 wins!"
            winner_group_teams = group1
            couter_group1_total += 1
        elif (couter_group1 < couter_group2):
            winner_group = "Group 2 wins!"
            winner_group_teams = group2
            couter_group2_total += 1
        else:
            winner_group = "Draw between Group 1 and Group 2"
            winner_group_teams = group1 + group2
            couter_group1_total += 1
            couter_group2_total += 1
        winner_msg = """Game over!
                        Group 1 typed in {} characters. Group 2 typed in {} characters.
                        {} 

                        Congratulations to the winners:
                        ==
                        {}""".format(couter_group1, couter_group2, winner_group, winner_group_teams).encode('ascii')
        statistic_msg = "The most commun character is {}".format(max(a_dict.items(), key=operator.itemgetter(1))[0]).encode('ascii')
        return winner_msg, statistic_msg

    def init_variable():
        global team_map, group1_ips, group2_ips, couter_group1, couter_group2
        team_map = {'group 1': [], 'group 2': []}
        group1_ips = []
        group2_ips = []
        couter_group1 = 0
        couter_group2 = 0

    def main():
        global group1_ips, group2_ips, team_map, couter_group1, couter_group2, a_dict, couter_group1_total, couter_group2_total,\
            total_games, most_commun_char, group1, group2
        while True:
            total_games += 1
            t1 = Thread(name='udp', target=send_udp_broadcast, daemon=True)
            t1.start()
            t_end = time.time() + 10
            while time.time() < t_end:
                events = sel.select(timeout=(t_end - time.time()))
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        if mask & selectors.EVENT_READ:
                            recv_data = key.fileobj.recv(1024).decode("utf-8")  # Should be ready to read
                            if recv_data:
                                create_team(key, mask, recv_data)
                            else:
                                try:
                                    sel.unregister(key.fileobj)
                                    key.fileobj.close()
                                    print(Magenta + Bold + 'closing connection to', key.data.addr)
                                except:
                                    pass

            t1.join()
            print(Magenta + Bold + "group1 = ", group1)
            print(Red + Bold + "group2 = ", group2)

            display_team()

            t_end = time.time() + 10
            while time.time() < t_end:
                events = sel.select(timeout=(t_end - time.time()))
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        sock = key.fileobj
                        data = key.data
                        get_char_from_client(sock, data, mask)

            winner_msg, statistic_msg = display_game_result()

            for client in team_map.get('group 1'):
                send_game_over(client[1], client[2], winner_msg)
            for client in team_map.get('group 2'):
                send_game_over(client[1], client[2], winner_msg)

            init_variable()

            print(Cyan + "“Game over, sending out offer requests...")



    if __name__ == '__main__':
        main()