#!/usr/bin/env python3

from uvk5 import UVK5, argv, eprint, Firmware

def main(cmd):
    argc = len(argv)
    fw = Firmware.load(argv[2])

    eprint('Version:', fw.version)

    if argc < 3:
        return

    if cmd == 'mod':
        eprint('mods:', argv[3])
        fw.apply_mods(argv[3].split(','))
        fw.write()
        if argc == 5:
            with UVK5(argv[4]) as uvk5:
                uvk5.get_version()
                uvk5.send_firmware(fw)
        return

    if cmd == 'cmp':
        fw2 = Firmware.load(argv[3])
        fw.compare(fw2)



if __name__ == '__main__':
    main(argv[1])
