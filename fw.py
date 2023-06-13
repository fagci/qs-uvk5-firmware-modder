#!/usr/bin/env python3

from uvk5 import UVK5, argv, eprint, Firmware

def main(cmd):
    argc = len(argv)
    fw = Firmware.load(argv[2])

    eprint('Version:', fw.version)

    if argc < 3:
        return

    if cmd == 'mod':
        if argc == 3:
            print('Mods:', ','.join(list(fw.get_available_mods())))
            return
        eprint('mods:', argv[3])
        fw.apply_mods(argv[3].split(','))
        fw.write()
        if argc == 5:
            with UVK5(argv[4]) as uvk5:
                uvk5.get_version()
                uvk5.send_firmware(fw)

    if cmd == 'cmp':
        fw2 = Firmware.load(argv[3])
        fw.compare(fw2)

    if cmd == 'search':
        fw.search(argv[3].encode())


def usage():
    eprint('Usage:', argv[0], '<cmd>', '<fw.bin>', '[args...]')
    exit(255)


if __name__ == '__main__':
    if len(argv) == 1:
        usage()

    main(argv[1])
