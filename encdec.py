#!/usr/bin/env python3

from binascii import crc_hqx as crc16
from itertools import cycle
import os
from pathlib import Path
from sys import argv
from sys import stderr

# Structure of pre-encoded payload
# 8196 | 16      | ...  | 2   |
# data | version | data | crc |

KEY = Path('./key.bin').read_bytes()

V_START = 8192
V_END = V_START + 16
CRC_LEN = 2

def eprint(*args, **kwargs):
    print(*args, **kwargs, file=stderr)


def xor(var):
    return bytes(a ^ b for a, b in zip(var, cycle(KEY)))


def make_16byte_version(version):
    return bytes([ord(c) for c in version] + [0] * (16 - len(version)))


def decrypt(data):
    decrypted = xor(data)
    eprint('version:', decrypted[V_START:V_END].decode())
    return decrypted[:V_START] + decrypted[V_END:-CRC_LEN]


def encrypt(data, version='2.01.26'):
    v = make_16byte_version(version)
    encrypted = xor(data[:V_START] + v + data[V_START:])
    checksum = crc16(encrypted, 0).to_bytes(2, 'little')
    return encrypted + checksum


def usage(info = None):
    if info:
        eprint(info)
    eprint(f'Usage: {argv[0]} <e|d> filename.bin > raw.bin')
    eprint(f'  Example decode: {argv[0]} d k5_26_encrypted.bin > k5_26_raw.bin')
    eprint(f'  Example encode: {argv[0]} e k5_26_raw.bin > k5_26_encrypted.bin')
    exit(128)


def main():
    if len(argv) == 3:
        mode = argv[1]
        file_bytes = Path(argv[2]).read_bytes()

        if mode == 'd':
            os.write(1, decrypt(file_bytes))
            eprint('Success!')
            return

        if mode == 'e':
            os.write(1, encrypt(file_bytes))
            eprint('Success!')
            return

    usage()
        

if __name__ == '__main__':
    main()
