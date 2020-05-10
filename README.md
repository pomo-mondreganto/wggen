# wggen
Simple Wireguard config generator

To generate configurations, execute `run.py` script in the project root. Supported options:

```
./run.py -h
usage: run.py [-h] --server example.com [--server-number N]
              [--per-peer N | --single-peer] [--subnet 0.0.0.0/0]
              [--subnet-newbits N] --server-output SERVER_OUTPUT
              (--peers N | --range N-N | --list N,N,...)

Generate Wireguard configuration files

optional arguments:
  -h, --help            show this help message and exit
  --server example.com  Server public address
  --server-number N     Server number when using with multiple servers
                        (default 0)
  --per-peer N          Number of clients per one peer (default 2)
  --single-peer         Force a single peer (/32 subnet)
  --subnet 0.0.0.0/0    Main subnet to add clients to (default 10.60.0.0/16)
  --subnet-newbits N    Number of bits for peer number in subnet (default 8)
  --server-output SERVER_OUTPUT
                        A path to dump configs to
  --peers N             Peer count
  --range N-N           Range of peer numbers (inclusive)
  --list N,N,...        List of peer numbers
```
