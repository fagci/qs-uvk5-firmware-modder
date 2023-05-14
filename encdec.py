#!/usr/bin/env python3

import os
from pathlib import Path
from sys import argv

from lib.base import crctest, eprint, encrypt, decrypt


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
    file_bytes = Path(fname).read_bytes()
    
    if encdec == 'crc':
        crctest(file_bytes)
        return

    if encdec == 'd':
        decrypted = decrypt(file_bytes)
        os.write(1, bytes(decrypted))
        eprint('Success!')
        return

    if encdec == 'e':
        eprint('WARNING! encoding not working for now, as CRC not valid')
        encrypted = encrypt(file_bytes)
        os.write(1, bytes(encrypted))
        eprint('Success!')
        return

    usage()
        

if __name__ == '__main__':
    main()
