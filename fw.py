#!/usr/bin/env python3

from uvk5 import argv, eprint, Firmware

def main(path):
    fw = Firmware.load(path)
    eprint('Version:', fw.version)
    if len(argv) == 4 and argv[2] == 'mod':
        eprint('mods:', argv[3])
        fw.apply_mods(argv[3].split(','))
        fw.write()

if __name__ == '__main__':
    main(argv[1])
