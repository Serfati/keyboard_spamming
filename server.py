import random
import selectors
import socket
import struct
import time
import types
from threading import Thread

from config import *

group1_key, group2_key = 'group 1', 'group 2'
team_map = {group1_key: [], group2_key: []}
group1_ips, group2_ips = [], []
group1, group2 = [], []
counter_group1, counter_group2 = 0, 0
total_games = 0
high_score = 0


sel = selectors.DefaultSelector()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lsock:
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    lsock.bind((host, port))
    lsock.listen()
    print(Bold, 'Server started, listening on IP address ', host, RESET)
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    def accept_wrapper(sock):
        try:
            conn, address = sock.accept()  # Should be ready to read
            print(Green, 'accepted connection from', RESET, address)
            conn.setblocking(False)
            data = types.SimpleNamespace(addr=address, inb=b'', outb=b'')
            sel.register(conn, selectors.EVENT_READ |
                         selectors.EVENT_WRITE, data=data)
        except:
            pass

    def send_udp_broadcast():
        magic = [0xfe, 0xed, 0xbe, 0xef]
        m_type = [0x02]
        host_port = struct.pack('>H', port)
        msg = bytes(magic) + bytes(m_type) + bytes(host_port)
        ip_start = host[:host.rfind('.') + 1]
        ip_range_list = ['{}{}'.format(ip_start, x) for x in range(0, 256)]
        time_end = time.time() + udp_time
        while time.time() < time_end:
            for ip in ip_range_list:
                sock = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(msg, (ip, port))
                sock.close()

    def create_team(key, mask, recv_data):
        global group1_ips, group2_ips, group1, group2
        if len(team_map.get(group1_key)) == len(team_map.get(group2_key)):
            group, arr = random.choice(list(team_map.items()))
            team_map[group].append((recv_data, key, mask))
            if group == group1_key:
                group1_ips.append(key.data.addr)
                group1.append(arr[0][0][:-1])
            else:
                group2_ips.append(key.data.addr)
                group2.append(arr[0][0][:-1])
        elif len(team_map.get(group1_key)) < len(team_map.get(group2_key)):
            team_map[group1_key].append((recv_data, key, mask))
            group1_ips.append(key.data.addr)
            group1.append(recv_data)
        elif len(team_map.get(group2_key)) < len(team_map.get(group1_key)):
            team_map[group2_key].append((recv_data, key, mask))
            group2_ips.append(key.data.addr)
            group2.append(recv_data)

    def get_char_from_client(sock, data, mask):
        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(1024)  # Should be ready to read
                if recv_data:
                    update_counter(data)
                else:
                    sel.unregister(sock)
                    sock.close()
                    print(Yellow + Bold + 'closing connection to', data.addr)
            except:
                pass
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def update_counter(data):
        if data.addr in group1_ips:
            global counter_group1
            counter_group1 += 1
        elif data.addr in group2_ips:
            global counter_group2
            counter_group2 += 1

    def send_game_over(key, mask, msg):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            data.outb += msg
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]
                sel.unregister(sock)
                sock.close()
                print(Cyan + Bold + 'closing connection to', data.addr)

    def display_team():
        for client in team_map.get(group1_key) + team_map.get(group2_key):
            sock = client[1].fileobj
            data = client[1].data
            sent_client_start_msg(sock, data, client[1], client[2])

    def sent_client_start_msg(sock, data, key, mask):
        if mask & selectors.EVENT_READ:
            group1_names = ''.join([i[0] for i in team_map.get(group1_key)])
            group2_names = ''.join([i[0] for i in team_map.get(group2_key)])
            start_msg = f"Welcome to Keyboard Spamming Battle Royale.\n Group 1:\n ==\n " \
                        f"{group1_names}\n Group 2:\n ==\n {group2_names}\n " \
                        f"Start pressing keys on your keyboard as fast as you can!! "
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
            for conn in team_map.get(group1_key):
                if conn[1] == key:
                    team_map.get(group1_key).remove(conn)
            for conn in team_map.get(group2_key):
                if conn[1] == key:
                    team_map.get(group2_key).remove(conn)
            sel.unregister(sock)
            sock.close()
            print(Magenta + Bold + 'closing connection to', data.addr)
        except:
            pass

    def display_game_result():
        global counter_group1, counter_group2
        if counter_group1 > counter_group2:
            win_group = "Group 1 wins!"
            winner_group_teams = ''.join(
                [i[0] for i in team_map.get(group1_key)])
        elif counter_group1 < counter_group2:
            win_group = "Group 2 wins!"
            winner_group_teams = ''.join(
                [i[0] for i in team_map.get(group2_key)])
        else:
            win_group = "Draw between Group 1 and Group 2"
            winner_group_teams = ''.join([i[0] for i in team_map.get(
                group1_key)]) + ''.join([i[0] for i in team_map.get(group2_key)])
        winner_msg = f"Game over!\nGroup 1 typed in {counter_group1} characters. Group 2 typed in {counter_group2} characters.\n" \
                     f"{win_group} \n" \
                     f"Congratulations to the winners:\n==\n{winner_group_teams}\n"
        return winner_msg.encode('ascii')

    def init_variable():
        global team_map, group1_ips, group2_ips, counter_group1, counter_group2, group1, group2
        team_map = {'group 1': [], 'group 2': []}
        group1_ips, group2_ips = [], []
        group1, group2 = [], []
        counter_group1, counter_group2 = 0, 0

    def stats():
        global high_score, total_games, team_map, group1_ips, group2_ips, counter_group1, counter_group2, group1, group2
        total_games += 1
        high_score = max(high_score, counter_group1, counter_group2)
        print()
        print(Blue, BgWhite,)
        print('+'+'-'*48+'+')
        print('|'+' '*18+'Server Stats'+' '*18+'|')
        print('+'+'-'*48+'+',end='')
        print(RESET)
        print(White, '\n* Total games played on server: {}'.format(total_games))
        print('* Highest score: {} keys'.format(high_score))
        try:
            print('* Group 1 achived {0:.2f}% from the points'.format(
                (counter_group1/(counter_group1+counter_group2) * 100)))
            print('* Group 2 achived {0:.2f}% from the points'.format(
                (counter_group2/(counter_group1+counter_group2)) * 100))
        except:
            pass
        print(RESET)
        print(Blue, '+'+'-'*48+'+', RESET)
        print()

    def main():
        global group1_ips, group2_ips, team_map, counter_group1, counter_group2, group1, group2

        while True:
            t1 = Thread(name='udp', target=send_udp_broadcast, daemon=True)
            t1.start()
            t_end = time.time() + udp_time
            while time.time() < t_end:
                events = sel.select(timeout=(t_end - time.time()))
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        if mask & selectors.EVENT_READ:
                            recv_data = key.fileobj.recv(1024).decode(
                                "utf-8")  # Should be ready to read
                            if recv_data:
                                create_team(key, mask, recv_data)
                            else:
                                try:
                                    sel.unregister(key.fileobj)
                                    key.fileobj.close()
                                    print(Magenta + Bold +
                                          'closing connection to', key.data.addr)
                                except:
                                    pass
            t1.join()
            print(Magenta + Bold + "group1 = ", group1)
            print(Red + Bold + "group2 = ", group2)
            display_team()
            time_end = time.time() + game_time
            while time.time() < time_end:
                events = sel.select(timeout=(time_end - time.time()))
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        sock = key.fileobj
                        data = key.data
                        get_char_from_client(sock, data, mask)

            for client in team_map.get(group1_key) + team_map.get(group2_key):
                send_game_over(client[1], client[2],  display_game_result())

            stats()
            init_variable()

            print(Cyan + "Game over, sending out offer requests...", RESET)

    if __name__ == '__main__':
        main()
