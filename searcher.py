#!/usr/bin/env python3

from pathlib import Path
from sys import argv

V_START = 8192

def main():
    if len(argv) != 3:
        print(f'Usage: {argv[0]} decrypted_file.bin <search_string>')
        exit(128)

    data = Path(argv[1]).read_bytes()
    search_for = argv[2].encode()

    if data[:4] != b'\x88\x13\x00\x20':
        print('Encrypted file, choose decrypted.')
        exit(200)

    search_for_len = len(search_for)

    for i in range(len(data)):
        if data[i:i+search_for_len] == search_for:
            print(f'[{i}]: {data[i:i+32]}')

if __name__ == '__main__':
    main()
