#!/usr/bin/env python3

from pathlib import Path
from sys import argv

def main(path, value, size):
    p = Path(path)
    sz = p.stat().st_size
    with p.open('rb') as f:
        for offset in range(sz):
            f.seek(offset)
            if offset + size > sz:
                break
            bb = f.read(size)
            v = int.from_bytes(bb, 'little')
            if v == value:
                print('0x%X: %d, hex: %s'%(offset, v, bb.hex()))


if __name__ == '__main__':
    main(argv[1], int(argv[2]), int(argv[3]) if len(argv) == 4 else 4)
