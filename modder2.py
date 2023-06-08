#!/usr/bin/env python3

import os
from pathlib import Path
from sys import argv

from lib.encdec import decrypt, encrypt, eprint

class Firmware:
    VERSION = 'unknown'

    @classmethod
    def load(cls, encrypted_file_path):
        file_bytes = Path(encrypted_file_path).read_bytes()
        decrypted, version = decrypt(file_bytes)
        eprint('version:', version)
        return globals()['%s_%s' %('Firmware', version.replace('.', '_'))](decrypted)


    def __init__(self, decrypted) -> None:
        self.decrypted = decrypted
        self.src_size = len(decrypted)

    def patch(self, mods):
        eprint('Not implemented yet')
        exit(128)

    def patch_single(self, addr, new_value, size=4):
        old_bytes = self.decrypted[addr:addr+size]
        old_value = int.from_bytes(old_bytes, 'little')
        new_bytes = int(new_value).to_bytes(size, 'little')
        self.decrypted = self.decrypted[:addr] + new_bytes + self.decrypted[addr+size:]


    def write(self, path=None):
        if self.src_size != len(self.decrypted):
            eprint('Something goes wrong. Check values or open issue.')
            exit(255)

        encrypted = encrypt(self.decrypted, self.VERSION)

        if path:
            pass
        else:
            os.write(1, encrypted)

class Firmware_2_01_26(Firmware):
    VERSION = '2.01.26'

    ADDRESSES = {
        'bands': [
            [0xE074, 0xE090],
            [0xE078, 0xE094],
            [0xE07C, 0xE098],
            [0xE080, 0xE09C],
            [0xE084, 0xE0A0],
            [0xE088, 0xE0A4],
            [0xE08C, 0xE0A8],
        ],
        'limits': [0x150C, 0x1510],
    }


def main(encrypted_file_path):
    fw = Firmware.load(encrypted_file_path)
    fw.patch({
        'bands': {
            2: [1800000, None],
            7: [None, 130000000],
        },
        'limits': [1800000, 130000000]
    })
    fw.write()


if __name__ == "__main__":
    main(argv[1])
