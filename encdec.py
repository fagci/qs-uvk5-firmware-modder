#!/usr/bin/env python3

import os
from pathlib import Path
from sys import argv

from lib.encdec import eprint, encrypt, decrypt


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
            decrypted, version = decrypt(file_bytes)
            eprint('version:', version)
            os.write(1, decrypted)
            eprint('Success!')
            return

        if mode == 'e':
            os.write(1, encrypt(file_bytes))
            eprint('Success!')
            return

    usage()
        

if __name__ == '__main__':
    main()
