#!/usr/bin/env python3

from pathlib import Path
from sys import argv

V_START = 8192

def main():
    if len(argv) != 3:
        print(f'Usage: {argv[0]} <search_string> decrypted_file.bin')
        exit(128)

    search_for = argv[1].encode()
    data = Path(argv[2]).read_bytes()

    if data[V_START:V_START+4] != b'2.01':
        print('Encrypted file, choose decrypted.')
        exit(200)

    search_for_len = len(search_for)

    for i in range(len(data)):
        if data[i:i+search_for_len] == search_for:
            print(f'[{i}]: {data[i:i+32]}')

if __name__ == '__main__':
    main()
