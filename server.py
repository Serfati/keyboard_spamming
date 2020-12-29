import selectors
import socket
import types
from threading import Thread
import time
from config import *
import random

team_map = {'group 1': [], 'group 2': []}
group1_ips = []
group2_ips = []
couter_group1 = 0
couter_group2 = 0
a_dict= {}
couter_group1_total=0
couter_group2_total=0
total_games=0

sel = selectors.DefaultSelector()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lsock:
    lsock.bind((host, port))
    lsock.listen()
    print(bcolors.BOLD, 'Server started, listening on IP address ', host, bcolors.RESET)
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)


    def accept_wrapper(sock):
        conn, addr = sock.accept()  # Should be ready to read
        print(bcolors.OKGREEN, 'accepted connection from', bcolors.RESET, addr)
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
                if (len(team_map.get('group 1')) < len(team_map.get('group 2'))):
                    team_map['group 1'].append((recv_data, key, mask))
                    group1_ips.append(data.addr)
                elif (len(team_map.get('group 2')) > len(team_map.get('group 1'))):
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
                    print(bcolors.BackgroundBrightMagenta + bcolors.BOLD + 'closing connection to', data.addr)
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
                        print(bcolors.BackgroundBrightMagenta + bcolors.BOLD + 'closing connection to', data.addr)
                    except:
                        pass


    def get_char_from_client(key, mask):
        global couter_group1
        global couter_group2
        global char_most
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                if recv_data.decode('ascii') in a_dict:
                    a_dict[recv_data.decode('ascii')] = a_dict[recv_data.decode('ascii')] + 1
                else:
                    a_dict[recv_data.decode('ascii')] = 1
                if (data.addr in group1_ips):
                    couter_group1 = couter_group1 + 1
                elif (data.addr in group2_ips):
                    couter_group2 = couter_group2 + 1
            else:
                try:
                    sel.unregister(sock)
                    sock.close()
                    print(a_dict)
                    print(bcolors.Yellow + bcolors.BOLD + 'closing connection to', data.addr)
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
                        print(bcolors.pink + bcolors.BOLD + 'closing connection to', data.addr)
                    except:
                        pass
                except:
                    try:
                        sel.unregister(sock)
                        sock.close()
                        print(bcolors.pink + bcolors.BOLD + 'closing connection to', data.addr)
                    except:
                        pass


    def send_fun_facts():
        print(bcolors.HEADER + bcolors.OKBLUE + "Some fun facts !!" + bcolors.RESET)
        try:
             char_most = max(a_dict, key=a_dict.get)
             print(bcolors.white + "the most typed char is", char_most)
        except:
             char_most = 0
        pgroup1=(couter_group1_total/total_games)*100
        print(bcolors.OKCYAN+"Group 1 has won in ", pgroup1, "percentage og the games")
        pgroup2 = (couter_group2_total / total_games) * 100
        print(bcolors.OKCYAN+"Group 2 has won in ", pgroup2, "percentage og the games")
        print(bcolors.purple+"The total games played on this server is", total_games)


    def send_udp_invaite():
        @dataclasses.dataclass
        class Msg:
            Magic_cookie: bytes
            Message_type: bytes
            Server_port: bytes

            def get_port_as_bytes(self):
                return self.Server_port

            def get_Message_type(self):
                return self.Message_type

            def get_Magic_cookie(self):
                return self.Magic_cookie

            def msg_to_bytes(self):
                return self.Magic_cookie + self.Message_type + self.Server_port

        frame = bytes([0xfe, 0xed, 0xbe, 0xef])
        type = bytes([0x02])
        s = struct.pack('>H', port)
        msg = Msg(frame, type, s).msg_to_bytes()
        t_end = time.time() + 10
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
        global group1_ips, group2_ips, team_map, couter_group1, couter_group2, a_dict, couter_group1_total, couter_group2_total, total_games

        while True:
            total_games+=1
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
            if (couter_group1 > couter_group2):
                winner_group = "Group 1 wins!"
                winner_group_teams = group1
                couter_group1_total+=1
            elif (couter_group1 < couter_group2):
                winner_group = "Group 2 wins!"
                winner_group_teams = group2
                couter_group2_total+=1
            else:
                winner_group = "Draw between Group 1 and Group 2"
                winner_group_teams = group1 + group2
                couter_group1_total+=1
                couter_group2_total+=1
            winner_msg = """Game over!
                            Group 1 typed in {} characters. Group 2 typed in {} characters.
                            {} 

                            Congratulations to the winners:
                            ==
                            {}""".format(couter_group1, couter_group2, winner_group, winner_group_teams).encode('ascii')

            for client in team_map.get('group 1'):
                send_game_over(client[1], client[2], winner_msg)
            for client in team_map.get('group 2'):
                send_game_over(client[1], client[2], winner_msg)

            team_map = {'group 1': [], 'group 2': []}
            group1_ips = []
            group2_ips = []
            couter_group1 = 0
            couter_group2 = 0
            send_fun_facts()
            print(bcolors.OKCYAN + "“Game over, sending out offer requests...")


    if __name__ == '__main__':
        main()