#!/usr/bin/env python3

from itertools import cycle
import os
from pathlib import Path
from sys import argv, stderr

# Structure of pre-encoded payload
# 8196 | 16      | ...  | 2   |
# data | version | data | crc |

KEY = Path('./key.bin').read_bytes()

V_OFFSET = 8192
V_LEN = 16
CRC_LEN = 2


def eprint(*args, **kwargs):
    print(*args, **kwargs, file=stderr)


def xor(var, key):
    return bytes(a ^ b for a, b in zip(var, cycle(key)))


def eprint_crc(crc):
    eprint('crc:', ['0x%02x' % x for x in crc], f'{crc[0]*crc[1]}')


def make_16yte_version(version):
    return bytes([ord(c) for c in version] + [0] * (16 - len(version)))


def decrypt(data):
    decr = xor(data, KEY)
    
    v = decr[V_OFFSET:V_OFFSET+V_LEN]
    decr_data = decr[:-CRC_LEN]
    crc = decr[-CRC_LEN:]

    eprint('version:', v)
    eprint_crc(crc)

    return decr_data


def encrypt(data, version='2.01.19'):
    v = make_16yte_version(version)
    data = data[:V_OFFSET] + v + data[V_OFFSET+V_LEN:]
    crc = b'\xd9\xab' # here will be some crc
    
    eprint('version:', v)
    eprint_crc(crc)

    return xor(data + crc, KEY)


def usage(info = None):
    if info:
        eprint(info)
    eprint(f'Usage: {argv[0]} <e|d> filename.bin > raw.bin')
    eprint(f'  Example decode: {argv[0]} d k5_26_encrypted.bin > k5_26_raw.bin')
    eprint(f'  Example encode: {argv[0]} e k5_26_raw.bin > k5_26_encrypted.bin')
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
        eprint('Success!')
        return

    if encdec == 'e':
        eprint('WARNING! encoding not working for now, as CRC not valid')
        decrypted = Path(fname).read_bytes()
        encrypted = encrypt(decrypted)
        os.write(1, bytes(encrypted))
        eprint('Success!')
        return

    usage()
        

if __name__ == '__main__':
    main()
