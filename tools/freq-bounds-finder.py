#!/usr/bin/env python3

from pathlib import Path
from sys import argv

INT_SIZE = 4

F0 = 47000000
F1 = 60000000

def main(path):
    p = Path(path)
    sz = p.stat().st_size
    with p.open('rb') as f:
        for offset in range(sz):
            f.seek(offset)
            if offset + INT_SIZE > sz:
                break
            v = int.from_bytes(f.read(INT_SIZE), 'little')
            if v == F0:
                print('0x%X: %d'%(offset, F0))
            if v == F1:
                print('0x%X: %d'%(offset, F1))


if __name__ == '__main__':
    main(argv[1])
