#!/usr/bin/env python3

from uvk5 import UVK5, argv, eprint, Firmware

def main(path):
    fw = Firmware.load(path)
    argc = len(argv)
    eprint('Version:', fw.version)
    if argc >= 4 and argv[2] == 'mod':
        eprint('mods:', argv[3])
        fw.apply_mods(argv[3].split(','))
        fw.write()
        if argc == 5:
            with UVK5(argv[4]) as uvk5:
                uvk5.get_version()
                uvk5.send_firmware(fw)

if __name__ == '__main__':
    main(argv[1])
