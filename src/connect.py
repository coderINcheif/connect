import nmap
import socket
from .ui import UI
from .utils import *
from .server import Server
from .client import Client


class Connect:
    def __init__(self):
        self.ip: str = get_ip_address()
        self.network_ip: str = f'{self.ip}/24'

    def start(self):
        while True:
            action = UI.prompt_action()
            self.init_server() if action == Action.SEND else self.init_client()

    def init_server(self):
        with Server(self.ip) as server:
            while True:
                spinner = UI.get_spinner('Waiting for receiver to connect ')
                while not server.is_connected:
                    server.connect_to_client()
                UI.stop_spinner(spinner)
                UI.display_message(f'Connected to {server.conn_addr}')

                skip_prompt = True
                while skip_prompt or UI.prompt_follow_up_action() != FollowUpAction.RETURN_HOME:
                    skip_prompt = False
                    filepath = UI.get_file()
                    server.notify_client()
                    server.transfer_file(filepath)
                    UI.display_message("Done")

                server.notify_client(dispose=True)
                server.dispose()
                return

    def init_client(self):
        with Client(self.ip) as client:
            spinner: SpinnerThread = UI.get_spinner("Finding devices")
            hosts = client.scan_network(self.network_ip)
            UI.stop_spinner(spinner)
            if len(hosts) == 0:
                UI.display_message("No devices found to receive files from")
                return
            server_ip = UI.prompt_hosts(hosts)
            client.connect(server_ip)

            while client.is_connected:
                spinner: SpinnerThread = UI.get_spinner('Waiting for sender')
                client.listen_server_status()
                UI.stop_spinner(spinner)
                client.receive_file() if client.is_connected else None
                UI.display_message('Done')

            UI.display_message("Connection closed by sender")
