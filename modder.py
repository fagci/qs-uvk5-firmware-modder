#!/usr/bin/env python3

from pathlib import Path
from sys import argv
from configparser import ConfigParser

from lib.encdec import decrypt, eprint

ADDR_DIR = Path(__file__).parent / 'addresses'

def main(encrypted_file_path):
    file_bytes = Path(encrypted_file_path).read_bytes()
    decrypted, version = decrypt(file_bytes)
    eprint('version:', version)

    addr_file = ADDR_DIR / ('%s.ini' % version)
    addresses = ConfigParser()
    addresses.read(addr_file)

    bands_addr = addresses['bands']
    for k in bands_addr:
        addr = int(bands_addr.get(k), 16)
        value = int.from_bytes(decrypted[addr:addr+4], 'little')
        eprint(k, addr, value)


if __name__ == "__main__":
    main(argv[1])
