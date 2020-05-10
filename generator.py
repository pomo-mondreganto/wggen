from typing import List

from netaddr import IPNetwork

from key import WGKey
from wg_config import WGConfig, ConfigSection


class WGGenerator:
    def __init__(self,
                 server: str,
                 server_number: int,
                 per_peer: int,
                 peer_list: List[int],
                 single_peer: bool,
                 subnet: str,
                 subnet_newbits: int):
        self.server = server
        self.server_number = server_number
        self.per_peer = per_peer
        self.peer_list = peer_list
        self.single_peer = single_peer
        self.subnet = IPNetwork(subnet)
        self.subnet_newbits = subnet_newbits

        need_bits = self.subnet.prefixlen + self.subnet_newbits
        self.peer_subnets = list(self.subnet.subnet(need_bits))

        self.server_key = WGKey.generate()
        self.peer_keys = {}
        self._generate_peer_keys()

        self.server_config = None
        self._generate_server_config()

        self.peer_configs = {}
        for peer in self.peer_list:
            self._generate_peer_configs(peer)

    def _generate_peer_keys(self):
        for peer in self.peer_list:
            self.peer_keys[peer] = WGKey.generate()

    def _generate_server_config(self):
        self.server_config = WGConfig()

        interface_section = ConfigSection(
            name='Interface',
            values={
                'Address': str(self.subnet[1]),
                'PrivateKey': self.server_key.private,
                'ListenPort': 30000 + self.server_number,
            },
        )
        self.server_config.add_section(interface_section)

        for peer in self.peer_list:
            cur_net = self.peer_subnets[peer]
            if self.single_peer:
                cur_net = list(cur_net.subnet(32))[2]

            peer_section = ConfigSection(
                name='Peer',
                values={
                    'PublicKey': self.peer_keys[peer].public,
                    'AllowedIPs': str(cur_net),
                }
            )
            self.server_config.add_section(peer_section)

    def _generate_peer_configs(self, peer):
        self.peer_configs[peer] = []
        per_peer = self.per_peer if not self.single_peer else 1

        for client in range(per_peer):
            client_addr = 2 + client
            ipc = WGConfig()

            if_addr = self.peer_subnets[peer][client_addr]
            interface_section = ConfigSection(
                name='Interface',
                values={
                    'Address': str(if_addr),
                    'PrivateKey': self.peer_keys[peer].private,
                    'ListenPort': 21000 + peer * self.per_peer + client,
                },
            )
            ipc.add_section(interface_section)

            peer_section = ConfigSection(
                name='Peer',
                values={
                    'PublicKey': self.server_key.public,
                    'Endpoint': self.server,
                    'AllowedIPs': '0.0.0.0/0',
                }
            )
            ipc.add_section(peer_section)
            ipc.add_value('PersistentKeepalive', 25)
            self.peer_configs[peer].append(ipc)
