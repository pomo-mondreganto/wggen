#!/usr/bin/env python3

import argparse
import re

from generator import WGGenerator

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Wireguard configuration files')

    parser.add_argument('--server', type=str, help='Server public address', required=True)
    parser.add_argument('--server-number', type=int, default=0, help='Server number (for multiple servers)')

    peer_group = parser.add_mutually_exclusive_group()
    peer_group.add_argument(
        '--per-peer', type=int,
        default=2, metavar='N',
        help='Number of clients per one peer',
    )
    peer_group.add_argument(
        '--single-peer', action='store_true',
        help='Force a single peer',
    )

    parser.add_argument(
        '--subnet', type=str,
        default='10.60.0.0/16', metavar='0.0.0.0/0',
        help='Main subnet to add clients to',
    )
    parser.add_argument(
        '--subnet-newbits', type=int,
        default=8, metavar='N',
        help='Number of bits for peer number in subnet',
    )

    parser.add_argument('--server-output', type=str, help='A path to dump configs to')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--peers', type=int, metavar='N', help='Peer count')
    group.add_argument('--range', type=str, metavar='N-N', help='Range of peer numbers (inclusive)')
    group.add_argument('--list', type=str, metavar='N,N,...', help='List of peer numbers')

    args = parser.parse_args()

    peers = None
    if args.peers:
        peers = list(range(1, args.peers + 1))
    elif args.range:
        match = re.search(r"(\d+)-(\d+)", args.range)
        if not match:
            print('Invalid range')
            exit(1)

        peers = list(range(int(match.group(1)), int(match.group(2)) + 1))
    else:
        peers = list(map(int, args.list.split(',')))

    generator = WGGenerator(
        server=args.server,
        server_number=args.server_number,
        per_peer=args.per_peer,
        peer_list=peers,
        single_peer=args.single_peer,
        subnet=args.subnet,
        subnet_newbits=args.subnet_newbits
    )

    print('Server:')
    print(generator.server_config.dumps())
    print('-' * 40)
    print('-' * 40)

    print('Clients:')

    for peer in peers:
        print('Peer', peer)
        print(('-' * 40 + '\n' + '-' * 40 + '\n').join(x.dumps() for x in generator.peer_configs[peer]))
        print('-' * 40)
        print('-' * 40)
