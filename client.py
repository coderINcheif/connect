import nmap
import socket
from settings import *


class Client():
    def __init__(self, ip: str):
        self.ip: str = ip
        self.port: int = CLIENT_PORT
        self.init_socket()

    def init_socket(self):
        self.socket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', self.port),)

    def scan_network(self, network_ip: str):
        scanner = nmap.PortScanner()
        scan = scanner.scan(
            network_ip, f'{SERVER_PORT}'
        )['scan']
        hosts = [
            (ip, stats['hostnames'][0]['name'])
            for ip, stats in scan.items() if stats['tcp'][8080]['state'] == 'open'
        ]
        return hosts

    def connect(self, server_ip: str):
        self.socket.connect((server_ip, SERVER_PORT),)

    def receive_file(self):
        # receiving filename
        filename = self.socket.recv(BUFFER_SIZE).decode('utf-8')
        self.socket.sendall(b'ack')

        # receiving file
        with open(f'./received/{filename}', 'wb') as f:
            complete_data = b''
            data = self.socket.recv(BUFFER_SIZE)
            complete_data += data
            while True:
                data = self.socket.recv(BUFFER_SIZE)
                if data.endswith(FIN_HEADER):
                    self.socket.sendall(b'ack')
                    break
                complete_data += data
            f.write(complete_data)

    def listen_server_status(self):
        header = self.socket.recv(BUFFER_SIZE)
        if header == DISPOSE_HEADER:
            self.dispose()

    @property
    def is_connected(self):
        return False if self.socket.fileno() < 0 else True

    def dispose(self):
        self.socket.close()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.dispose()