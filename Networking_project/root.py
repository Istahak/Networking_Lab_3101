import os
import socket
import threading
import struct

IP = '127.0.0.1'
PORT = 5426
ADDR = (IP, PORT)
tld=(IP,4488)
SIZE = 1024
FORMAT = "utf-8"
dns_records={
    "www.tictactoe.com":('12369','A',86400),
    "www.msgttt.com": ('5428','NS',86400),
    "www.google.com":('5428','NS',86400)
}

def encode_msg(message):
    data = message.split()
    name = data[0]
    type = data[1]
    flag = 0
    qq = 0
    aa = 1
    auth_rr = 0
    add_rr = 0

    message = (name + ' ' + type + ' ' + data[2] + ' ' + data[3]).encode('utf-8')
    res = struct.pack(f"6H{len(message)}s", 50, flag, qq, aa, auth_rr, add_rr, message)
    return res

def handle_client(data, addr,server):

    try:
        print(f"RECEIVED MESSAGE {data} from {addr}.")
        msg=encode_msg(str(data+' '+dns_records[data][0]+' '+dns_records[data][1]+' '+str(dns_records[data][2])))
        server.sendto(msg,addr)
    except Exception as e:
        print("ERROR: ",str(e))

def main():
   
    print("ROOT Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(ADDR)
    print(f"ROOT Server is listening on {IP}:{PORT}.")

    while True:
        data, addr = server.recvfrom(SIZE)
        data = data.decode(FORMAT)
        #thread = threading.Thread(target=handle_client, args=(data, addr,server))
        #thread.start()
        handle_client(data,addr,server)
        print(f"ACTIVE CONNECTIONS {threading.active_count() - 1}")

if __name__ == "__main__":
    main()
