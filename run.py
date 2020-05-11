#!/usr/bin/env python3

import argparse
import os
import re

from generation import WGGenerator

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Wireguard configuration files')

    parser.add_argument(
        '--server', type=str,
        metavar='example.com',
        help='Server public address', required=True,
    )
    parser.add_argument(
        '--server-number', type=int,
        metavar='N', default=0,
        help='Server number when using with multiple servers (default 0)',
    )

    peer_group = parser.add_mutually_exclusive_group()
    peer_group.add_argument(
        '--per-group', type=int,
        default=2, metavar='N',
        help='Number of clients per one group (or subnet) (default 2)',
    )
    peer_group.add_argument(
        '--single-peer', action='store_true',
        help='Force a single peer in each group (/32 subnet)',
    )

    parser.add_argument(
        '--subnet', type=str,
        default='10.60.0.0/16', metavar='0.0.0.0/0',
        help='Main subnet to add groups to (default 10.60.0.0/16)',
    )
    parser.add_argument(
        '--subnet-newbits', type=int,
        default=8, metavar='N',
        help='Number of bits for group subnet in base subnet (default 8)',
    )

    parser.add_argument('--server-output', type=str, help='A path to dump configs to', required=True)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--groups', type=int, metavar='N', help='Group count')
    group.add_argument('--range', type=str, metavar='N-N', help='Range of group numbers (inclusive)')
    group.add_argument('--list', type=str, metavar='N,N,...', help='List of group numbers')

    args = parser.parse_args()

    groups = None
    if args.groups:
        groups = list(range(1, args.groups + 1))
    elif args.range:
        match = re.search(r"(\d+)-(\d+)", args.range)
        if not match:
            print('Invalid range')
            exit(1)

        groups = list(range(int(match.group(1)), int(match.group(2)) + 1))
    else:
        groups = list(map(int, args.list.split(',')))

    generator = WGGenerator(server=args.server, server_number=args.server_number, per_group=args.per_group,
                            group_list=groups, single_peer=args.single_peer, subnet=args.subnet,
                            subnet_newbits=args.subnet_newbits)

    so_dir = args.server_output
    if not os.path.exists(so_dir):
        os.mkdir(so_dir)
    if not os.path.isdir(so_dir):
        print(f'Error! {so_dir} is not a directory')
        exit(1)

    if os.listdir(so_dir):
        print(f'Error! {so_dir} is not empty')
        exit(1)

    server_config_path = os.path.join(so_dir, f'server{args.server_number}.conf')
    with open(server_config_path, 'w') as f:
        f.write(generator.server_config.dumps())

    for group in groups:
        group_config_dir = os.path.join(so_dir, f'group{group:03}')
        os.mkdir(group_config_dir)

        for peer, conf in generator.peer_configs[group].items():
            peer_config_path = os.path.join(group_config_dir, f'group{group:03}_{peer + 1}.conf')
            with open(peer_config_path, 'w') as f:
                f.write(conf.dumps())
