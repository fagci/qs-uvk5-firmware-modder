#!/usr/bin/env python3

import os
from pathlib import Path
from itertools import cycle

from sys import argv, stderr

# Structure of pre-encoded payload
# 8196    | 16        | ...     | 2   |
# data D1 | version V | data D2 | crc |

KEY = Path('./key.bin').read_bytes()

D1_LEN = 8192
V_LEN = 16

def xor(var, key):
    return bytes(a ^ b for a, b in zip(var, cycle(key)))

def decrypt(data):

    decr = xor(data, KEY)
    
    d1 = decr[:D1_LEN]
    v = decr[D1_LEN:D1_LEN+V_LEN]
    d2 = decr[D1_LEN+V_LEN:-2]
    crc = decr[-2:]

    print('version:', v, file=stderr)
    print('crc:', ['0x%02x' % x for x in crc], f'{crc[0]*crc[1]}', file=stderr)

    return d1 + d2

def encrypt(data, version='2.01.26'):
    D1_LEN = 8192
    v = bytes([ord(c) for c in version] + [0] * (16 - len(version)))
    print('version:', v, file=stderr)
    return xor(data[:D1_LEN] + v + data[D1_LEN:] + b'\xd8\x7f', KEY)

def usage(info = None):
    if info:
        print(info, file=stderr)
    print(f'Usage: {argv[0]} <e|d> filename.bin > raw.bin', file=stderr)
    print(f'  Example decode: {argv[0]} d k5_26_encrypted.bin > k5_26_raw.bin', file=stderr)
    print(f'  Example encode: {argv[0]} e k5_26_raw.bin > k5_26_encrypted.bin', file=stderr)
    exit(128)

def main():
    if len(argv) != 3:
        usage()

    encdec = argv[1]
    fname = argv[2]

    if encdec == 'd':
        encrypted = Path(fname).read_bytes()
        decrypted = decrypt(encrypted)
        os.write(1, bytes(decrypted))
        print('Success!', file=stderr)
        return
    if encdec == 'e':
        print('WARNING! encoding not working for now, as CRC not valid', file=stderr)
        decrypted = Path(fname).read_bytes()
        encrypted = encrypt(decrypted)
        os.write(1, bytes(encrypted))
        print('Success!', file=stderr)
        return

    usage()
        

if __name__ == '__main__':
    main()
