import socket
import threading
import struct

IP = '127.0.0.1'
PORT = 5429
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
dns_records={
    "www.tictactoe.com":('18.26.26.3','A',86400),
    "www.msgttt.com": ('12358','A',86400),
    "www.google.com":('10.35.36.21','A',86400)
}

def encode_msg(message, flag):
    data = message.split()
    name = data[0]
    type = data[1]
    qq = 0
    aa = 1
    auth_rr = 0
    add_rr = 0

    message = (name + ' ' + type + ' ' + data[2] + ' ' + data[3]).encode('utf-8')
    res = struct.pack(f"6H{len(message)}s", 50, flag, qq, aa, auth_rr, add_rr, message)
    return res

def handle_client(data, addr, server):
    try:
        print(f"RECEIVED MESSAGE {data} from {addr}.")
        if(dns_records[data][1]=='NS'):
            msg=encode_msg(str(data+' '+dns_records[data][0]+' '+dns_records[data][1]+' '+str(dns_records[data][2])), 0)
            server.sendto(msg, addr)
        else:
            msg=encode_msg(str(data+' '+dns_records[data][0]+' '+dns_records[data][1]+' '+str(dns_records[data][2])), 1)
            server.sendto(msg,addr)
    except Exception as e:
        print("ERROR: ",str(e))
            

    


def main():
   
    print("Authorative Server is starting...")
    #Creating a UDP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(ADDR)
    print(f"Auth Server is listening on {IP}:{PORT}.")

    while True:
        data, addr = server.recvfrom(SIZE)
        data = data.decode(FORMAT)
        # thread = threading.Thread(target=handle_client, args=(data, addr,server))
        # thread.start()
        handle_client(data,addr,server)
        print(f"ACTIVE CONNECTIONS {threading.active_count() - 1}")

if __name__ == "__main__":
    main()
