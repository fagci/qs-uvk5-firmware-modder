#!/usr/bin/env python3

from uvk5 import argv, eprint, Firmware

def main(path):
    fw = Firmware.load(path)
    print('Version:', fw.version)

if __name__ == '__main__':
    main(argv[1])
