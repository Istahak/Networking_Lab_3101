import socket
import time 
import random

class TCPClient:
    def __init__(self, client):
        self.client_socket = client
        self.recv_buffer_size = 64
        self.mss = 8
        self.expected_seq_num = 0
        self.ack_num = 0
        self.start_time = 0
        self.buffer_data = b''
        self.received_data = b''

    def create_segment(self, seq_num=0, ack_num=0, ack=0, sf=0, rwnd=0, checksum=0):
        return seq_num.to_bytes(4, byteorder="little") + \
               ack_num.to_bytes(4, byteorder="little") + \
               ack.to_bytes(1, byteorder="little") + \
               sf.to_bytes(1, byteorder="little") + \
               rwnd.to_bytes(2, byteorder="little") + \
               checksum.to_bytes(2, byteorder="little")

    def extract_header(self, segment):
        return int.from_bytes(segment[:4], byteorder="little"), \
               int.from_bytes(segment[4:8], byteorder="little"), \
               int.from_bytes(segment[8:9], byteorder="little"), \
               int.from_bytes(segment[9:10], byteorder="little"), \
               int.from_bytes(segment[10:12], byteorder="little"), \
               int.from_bytes(segment[12:14], byteorder="little")

    def calculate_checksum(self, bytestream):
        if len(bytestream) % 2 == 1:
            bytestream += b'\x00'

        checksum = 0

        for i in range(0, len(bytestream), 2):
            chunk = (bytestream[i] << 8) + bytestream[i+1]
            checksum += chunk

            if checksum > 0xffff:
                checksum = (checksum & 0xffff) + 1

        return ~checksum & 0xffff

    def receive_data(self):
        # self.client_socket.connect((self.host, self.port))
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.recv_buffer_size)
        self.client_socket.settimeout(1)
        while True:
            try:
                header = self.client_socket.recv(14)
                # print(header.decode())
                seq_num, ack_num, ack, sf, rwnd, checksum = self.extract_header(header)
                if sf == 1:
                    self.client_socket.recv(3)
                    break
                if not header:
                    break
                data = self.client_socket.recv(self.mss)
                # print(data)
                if self.calculate_checksum(data) != checksum:
                    continue

            except socket.timeout:
                rwind = self.recv_buffer_size - (len(self.buffer_data) + self.mss - 1) // self.mss
                try:
                    to_send_ack = self.create_segment(self.expected_seq_num, self.ack_num, 1, 0, rwind, 0)
                    self.client_socket.sendall(to_send_ack)
                except:
                    print("Connection closed")
                continue

            if not data:
                break
            seq_num = self.ack_num
            val = random.randint(0, 50)
            if val > 2:
                if seq_num == self.expected_seq_num:
                    self.buffer_data += data
                    self.ack_num += len(data)
                    self.expected_seq_num += len(data)
                    to_send_ack = self.create_segment(seq_num, self.ack_num, 1, 0, 8, 0)
                    if len(self.buffer_data) >= self.recv_buffer_size:
                        self.received_data += self.buffer_data
                        self.buffer_data = b''
                        try:
                            self.client_socket.sendall(to_send_ack)
                        except:
                            print("Client closed")
                else:
                    print("Triple duplicate acknowledgment Happened. Sending acknowledgment.")
                    to_send_ack = self.create_segment(self.expected_seq_num, self.expected_seq_num, 1, 1, 0, 0)
                    self.client_socket.sendall(to_send_ack)
            elif val > 1:
                time.sleep(6)
            else:
                print("Triple duplicate acknowledgment Happened. Sending acknowledgment.")
                to_send_ack = self.create_segment(self.expected_seq_num, self.expected_seq_num, 1, 1, 0, 0)
                self.client_socket.sendall(to_send_ack)

        self.received_data += self.buffer_data
        result = self.received_data
        # print(self.received_data.decode())
        self.recv_buffer_size = 64
        self.mss = 8
        self.expected_seq_num = 0
        self.ack_num = 0
        self.start_time = 0
        self.buffer_data = b''
        self.received_data = b''
        return result
        # self.client_socket.close()

# Usage
if __name__ == '__main__':
    server_address = ('127.0.0.1', 8870)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    client.connect(server_address)
    client = TCPClient(client)
    print(client.receive_data())
    print("done");
    print(client.receive_data())
    
