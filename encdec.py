#!/usr/bin/env python3

from binascii import crc_hqx
from itertools import cycle
import os
from pathlib import Path
from sys import argv
from sys import stderr

# Structure of pre-encoded payload
# 8196 | 16      | ...  | 2   |
# data | version | data | crc |

KEY = Path('./key.bin').read_bytes()

V_OFFSET = 8192
V_LEN = 16
CRC_LEN = 2

def eprint(*args, **kwargs):
    print(*args, **kwargs, file=stderr)


def xor(var):
    return bytes(a ^ b for a, b in zip(var, cycle(KEY)))


def decrypt(data):
    decrypted = xor(data)
    eprint('version:', decrypted[V_OFFSET:V_OFFSET+V_LEN].decode())
    return decrypted[:-CRC_LEN]


def encrypt(data):
    encrypted = xor(data)
    checksum = crc_hqx(encrypted, 0).to_bytes(2, byteorder='little')
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
