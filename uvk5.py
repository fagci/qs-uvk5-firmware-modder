#!/usr/bin/env python3

from binascii import crc_hqx
from itertools import cycle
from sys import stderr, argv
from pathlib import Path
from time import time
from io import StringIO

from serial import Serial

DATA_DIR = Path(__file__).parent / 'data'

KEY_FW = (DATA_DIR / 'key-fw.bin').read_bytes()
KEY_COMM = (DATA_DIR / 'key-comm.bin').read_bytes()

V_START = 8192
V_END = V_START + 16
CRC_LEN = 2


def chunk(data, n):
    for i in range(0,len(data), n):
        yield data[i:i+n]


def eprint(*args, **kwargs):
    print(*args, **kwargs, file=stderr)


def xor(var):
    return bytes(a ^ b for a, b in zip(var, cycle(KEY_FW)))


def xor_comm(var):
    return bytes(a ^ b for a, b in zip(var, cycle(KEY_COMM)))


def make_16byte_version(version):
    return bytes([ord(c) for c in version] + [0] * (16 - len(version)))
    

def i2b16(val):
    return int(val).to_bytes(2,'little')
    

def i2b32(val):
    return int(val).to_bytes(4,'little')


def b2i(data):
    return int.from_bytes(data, 'little')


def len16(data):
    return i2b16(len(data))


def crc16(data):
    return i2b16(crc_hqx(data, 0))


def decrypt(data):
    decrypted = xor(data)
    version = decrypted[V_START:V_END].decode().rstrip('\x00')
    return (decrypted[:V_START] + decrypted[V_END:-CRC_LEN], version)


def encrypt(data, version='2.01.26'):
    v = make_16byte_version(version)
    encrypted = xor(data[:V_START] + v + data[V_START:])
    checksum = crc16(encrypted)
    return encrypted + checksum


class UVK5(Serial):
    BLOCK_SIZE = 0x80

    PREAMBLE = b'\xab\xcd'
    POSTAMBLE = b'\xdc\xba'

    CMD_VERSION_REQ = 0x0514
    CMD_VERSION_RES = 0x0515
    CMD_SETTINGS_REQ = 0x051B
    CMD_SETTINGS_RES = 0x051C

    CMD_SETTINGS_WRITE_REQ = 0x051D # then addr (0x0E70) then size (0x0160) then data

    def __init__(self, port: str | None = None) -> None:
        self.timestamp = i2b32(time())
        super().__init__(port, 38400, timeout=5)

    def get_version(self):
        return self.cmd(UVK5.CMD_VERSION_REQ)[1][:10].decode().rstrip('\x00')

    def read_mem(self, offset, size):
        return self.cmd(UVK5.CMD_SETTINGS_REQ, i2b16(offset) + i2b16(size))

    def cmd(self, id, body = b''):
        self.write(self._cmd_make_req(id, body))
        preamble = self.read(2)

        if preamble != UVK5.PREAMBLE:
            raise ValueError('Bad response (PRE)', preamble)

        payload_len = b2i(self.read(2)) + 2 # CRC len
        payload = xor_comm(self.read(payload_len))

        # crc = payload[-2:]
        postamble = self.read(2)
        
        if postamble != UVK5.POSTAMBLE:
            raise ValueError('Bad response (POST)')
            
        # print(data.hex())
        cmd_id = b2i(payload[:2])
        data_len = b2i(payload[2:4])
        data = payload[4:4+data_len]

        return (cmd_id, data)

    def channels(self):
        names = []
        settings = []

        data_size = 16 * 200
        names_offset = 0x0F50
        settings_offset = 0x0000

        passes = data_size//UVK5.BLOCK_SIZE

        out = StringIO()

        for block in range(passes):
            offset = names_offset + block*UVK5.BLOCK_SIZE
            names_set = self.read_mem(offset, UVK5.BLOCK_SIZE)[1][4:]
            names += [name.decode(errors='ignore').rstrip('\x00') for name in chunk(names_set, 16)]

        for block in range(passes):
            offset = settings_offset + block*UVK5.BLOCK_SIZE
            settings_set = self.read_mem(offset, UVK5.BLOCK_SIZE)[1][4:]
            settings += [(b2i(setting[:4])/100000.0, ) for setting in chunk(settings_set, 16)]
        
        for i, name in enumerate(names):
            if name:
                print(f'{i+1:0>3}. {name: <16} {settings[i][0]:0<8} M', file=out)
            else:
                print(f'{i+1:0>3}. -', file=out)

        return out.getvalue()


    def _cmd_make_req(self, cmd_id, body=b''):
        data = body + self.timestamp
        payload = i2b16(cmd_id) + len16(data) + data
        encoded_payload = xor_comm(payload + crc16(payload))

        return UVK5.PREAMBLE + len16(payload) + encoded_payload + UVK5.POSTAMBLE


if __name__ == '__main__':
    if len(argv) < 3:
        eprint(f'Usage: {argv[0]} <port> <command:(channels|version)> [args]')
        exit(255)

    port = argv[1]
    cmd = argv[2]
    args = argv[3:]

    with UVK5(port) as s:
        version = s.get_version()
        if cmd == 'version':
            print('FW Version:', version)
            exit(0)

        print(getattr(s, cmd)(*args))

