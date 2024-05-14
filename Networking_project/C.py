import socket
import time
import os

class TCPServer:
    def __init__(self, client):
        print("Server is listening...")
        self.client_socket = client
        self.client_socket.settimeout(100)
        print(f"Connected to server on address")

    def toHeader(self, seqNum=0, ackNum=0, ack=0, sf=0, rwnd=0, chcksum=0):
        return seqNum.to_bytes(
            4, byteorder="little") + ackNum.to_bytes(
                4, byteorder="little") + ack.to_bytes(
                    1, byteorder="little") + sf.to_bytes(
                        1, byteorder="little") + rwnd.to_bytes(
                            2, byteorder="little") + chcksum.to_bytes(
                                2, byteorder="little")

    def fromHeader(self, segment):
        return int.from_bytes(
            segment[:4], byteorder="little"), int.from_bytes(
                segment[4:8], byteorder="little"), int.from_bytes(
                    segment[8:9], byteorder="little"), int.from_bytes(
                        segment[9:10], byteorder="little"), int.from_bytes(
                            segment[10:12], byteorder="little"), int.from_bytes(
                                segment[12:14], byteorder="little")

    def calculate_checksum(self, bytestream):
        if len(bytestream) % 2 == 1:
            bytestream += b'\x00'

        checksum = 0

        for i in range(0, len(bytestream), 2):
            chunk = (bytestream[i] << 8) + bytestream[i + 1]
            checksum += chunk

            if checksum > 0xffff:
                checksum = (checksum & 0xffff) + 1

        return ~checksum & 0xffff

    def send_data(self, data):
        mss = 8
        recv_buffer = 50
        timeout = 5
        file_size = len(data)
        cwnd = mss
        ssthresh = 8  # Initial Slow Start threshold
        seq_num = 0
        last_ack = 0
        dup_ack = 0
        window_len = 2 * recv_buffer
        start_time = time.time()
        timeout_start = start_time
        while seq_num < file_size:
            curr = 0
            print(f"Packets sending. Window value: {cwnd}")
            while curr < window_len and seq_num < file_size:
                send_size = min(mss, len(data) - seq_num)
                self.client_socket.sendall(self.toHeader(seq_num, seq_num, 0, 0, 0,
                                                    self.calculate_checksum(data[seq_num:seq_num + send_size])) + data[
                                       seq_num:seq_num + send_size])
                curr += send_size
                seq_num += send_size

            try:
                header = self.client_socket.recv(14)
                seqNum, ack_num, ack, sf, rwnd, chcksum = self.fromHeader(header)
            except:
                ssthresh = cwnd // 2
                cwnd = mss
                seq_num = last_ack
                print("Timeout")
                start_time = time.time()

            window_len = min(cwnd, rwnd)
            if ack_num == last_ack:
                dup_ack += 3
            else:
                dup_ack = 0

            if ack_num == seq_num:
                start_time = time.time()
                if cwnd >= ssthresh:
                    cwnd += mss
                else:
                    cwnd = min(2 * cwnd, ssthresh)

            if dup_ack == 3:
                dup_ack = 0
                ssthresh = cwnd // 2
                cwnd = ssthresh
                seq_num = last_ack

            last_ack = ack_num

            if time.time() - start_time > timeout:
                ssthresh = cwnd // 2
                cwnd = mss
                seq_num = last_ack
                print("Timeout!!!")
                start_time = time.time()
        self.client_socket.sendall(self.toHeader(seq_num, seq_num, 0, 1, 0,
                                                    self.calculate_checksum(data[seq_num:seq_num + send_size])) + "end".encode())
        # self.client_socket.close()

# Usage

        # self.client_socket.close()

# Usages
if __name__ == "__main__":
    server_address = ('127.0.0.1', 8870)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(server_address)
    server_socket.listen()
    client_socket, client_address = server_socket.accept()
    print(f"Connencted with {client_address}")
    tcp_client = TCPServer(client_socket)
    
    data = b"Hello boy are you okay?"
    tcp_client.send_data(data)
    data1 = b"Annie are you okay?"
    print("second")
    tcp_client.send_data(data1)
