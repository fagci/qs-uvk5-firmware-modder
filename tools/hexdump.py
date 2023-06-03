#!/usr/bin/env python3

from functools import partial
from pathlib import Path
from string import digits, ascii_letters, punctuation
from sys import argv

PRINTABLE = digits + ascii_letters + punctuation + " "

def main(file):
    pr = list(map(ord, PRINTABLE))

    with Path(file).open('rb') as f:
        for i, block in enumerate(iter(partial(f.read, 16), b'')):
            row = ['%02X'%c for c in block]
            chars = [chr(c) if c in pr else '·' for c in block]
            
            print('0x%06x'%(i*16), end='  ')
            print(*row, sep=' ', end='  ')
            print(*chars, sep='')
            
if __name__ == "__main__":
    main(argv[1])
