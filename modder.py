#!/usr/bin/env python3

import os
from pathlib import Path
from sys import argv
from configparser import ConfigParser

from lib.encdec import decrypt, encrypt, eprint

ADDR_DIR = Path(__file__).parent / 'addresses'
MODS_DIR = Path(__file__).parent / 'mods'

def main(encrypted_file_path):
    file_bytes = Path(encrypted_file_path).read_bytes()
    decrypted, version = decrypt(file_bytes)
    eprint('version:', version)

    addr_file = ADDR_DIR / ('%s.ini' % version)
    mods_file = MODS_DIR / ('%s.ini' % version)

    addresses = ConfigParser()
    mods = ConfigParser()
    addresses.read(addr_file)
    mods.read(mods_file)


    for section_name in addresses:
        eprint('[%s]' % section_name)
        section_values = addresses[section_name]
        for k in section_values:
            addr = int(section_values.get(k), 16)
            value = int.from_bytes(decrypted[addr:addr+4], 'little')
            eprint(k, addr, value)

            if mods[section_name] and mods[section_name].get(k):
                new_value = mods[section_name].get(k)
                eprint('new:', new_value)
                decrypted = decrypted[:addr] + int(new_value).to_bytes(4, 'little') + decrypted[addr+4:]


    encrypted = encrypt(decrypted, version)
    os.write(1, encrypted)



if __name__ == "__main__":
    main(argv[1])
