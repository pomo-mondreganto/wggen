from typing import List, Dict

from netaddr import IPNetwork

from .key import WGKey
from .wg_config import WGConfig, ConfigSection


class WGGenerator:
    def __init__(self, server: str, server_number: int, per_group: int, group_list: List[int], single_peer: bool,
                 subnet: str, subnet_newbits: int):
        self._server = server
        self._server_number = server_number
        self._per_group = per_group
        self._group_list = group_list
        self._single_peer = single_peer
        self._subnet = IPNetwork(subnet)
        self._subnet_newbits = subnet_newbits

        self._server_port = 30000 + self._server_number

        need_bits = self._subnet.prefixlen + self._subnet_newbits
        self._group_subnets = list(self._subnet.subnet(need_bits))

        self._server_key = WGKey.generate()
        self._peer_keys: Dict[int, Dict[int, WGKey]] = {}

        self.server_config = None
        self._peers_in_group = 1 if self._single_peer else self._per_group
        self.peer_configs: Dict[int, Dict[int, WGConfig]] = {}

        self._generate_peer_keys()
        self._generate_configs()

    def _generate_peer_keys(self):
        for group in self._group_list:
            self._peer_keys[group] = {}
            for peer in range(self._peers_in_group):
                self._peer_keys[group][peer] = WGKey.generate()

    def _generate_configs(self):
        self.server_config = WGConfig()

        interface_section = ConfigSection(
            name='Interface',
            values={
                'Address': str(self._subnet[1]),
                'PrivateKey': self._server_key.private,
                'ListenPort': self._server_port,
            },
        )
        self.server_config.add_section(interface_section)

        for group in self._group_list:
            cur_net = self._group_subnets[group]
            self.peer_configs[group] = {}

            for peer in range(self._peers_in_group):
                peer_subnet = list(cur_net.subnet(32))[2 + peer]
                peer_section = ConfigSection(
                    name='Peer',
                    values={
                        'PublicKey': self._peer_keys[group][peer].public,
                        'AllowedIPs': str(peer_subnet),
                    }
                )
                self.server_config.add_section(peer_section)

                peer_conf = WGConfig()

                peer_interface = ConfigSection(
                    name='Interface',
                    values={
                        'Address': str(peer_subnet[0]),
                        'PrivateKey': self._peer_keys[group][peer].private,
                        'ListenPort': 21000 + (self._server_number % 1000) * 1000 + group * self._per_group + peer,
                    },
                )
                peer_conf.add_section(peer_interface)

                endpoint_section = ConfigSection(
                    name='Peer',
                    values={
                        'PublicKey': self._server_key.public,
                        'Endpoint': f'{self._server}:{self._server_port}',
                        'AllowedIPs': '10.60.0.0/14, 10.80.0.0/14, 10.10.10.0/24',
                    },
                )
                peer_conf.add_section(endpoint_section)
                peer_conf.add_value('PersistentKeepalive', 25)

                self.peer_configs[group][peer] = peer_conf
