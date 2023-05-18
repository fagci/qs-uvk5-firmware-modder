#!/usr/bin/env python3

from binascii import crc_hqx
from itertools import cycle
from sys import argv
from time import time

from serial import Serial

KEY = bytes.fromhex('166c14e62e910d402135d5401303e980')
BLOCK_SIZE = 0x80

PREAMBLE = b'\xab\xcd'
POSTAMBLE = b'\xdc\xba'

CMD_VERSION_REQ = 0x0514
CMD_VERSION_RES = 0x0515

CMD_SETTINGS_REQ = 0x051B
CMD_SETTINGS_RES = 0x051C

TIMESTAMP = int(time()).to_bytes(4, 'little')


def xor(var):
    return bytes(a ^ b for a, b in zip(var, cycle(KEY)))
    

def i2b16(cmd_id):
    return cmd_id.to_bytes(2,'little')


def b2i(data):
    return int.from_bytes(data, 'little')


def len16(data):
    return i2b16(len(data))


def crc16(data):
    return i2b16(crc_hqx(data, 0))


def cmd_make_req(cmd_id, body=b''):
    data = body + TIMESTAMP
    payload = i2b16(cmd_id) + len16(data) + data
    encoded_payload = xor(payload + crc16(payload))

    return PREAMBLE + len16(payload) + encoded_payload + POSTAMBLE


def cmd_resp(cmd_id, data):
    # print('%x'%cmd_id)
    if cmd_id == CMD_VERSION_RES:
        print('FW version:', data[:10].decode())
        return

    if cmd_id == CMD_SETTINGS_RES:
        channels_offset = b2i(data[:2])
        channels_size = b2i(data[2:4])
        print(f'Channels({channels_offset}, {channels_size}):')
        channel_names = data[4:]
        for i in range(len(channel_names)//16):
            print(channel_names[i*16:(i+1)*16].decode(errors='ignore'))
        return


class UVK5(Serial):
    def __init__(self, port: str | None = None) -> None:
        super().__init__(port, 38400, timeout=5)

    def read_mem(self, offset, size):
        return self.cmd(CMD_SETTINGS_REQ, i2b16(offset) + i2b16(size))

    def cmd(self, id, body = b''):
        self.write(cmd_make_req(id, body))
        preamble = self.read(2)

        if preamble != PREAMBLE:
            raise ValueError('Bad response (PRE)')

        payload_len = b2i(self.read(2)) + 2 # CRC len
        payload = xor(self.read(payload_len))

        # crc = payload[-2:]
        postamble = self.read(2)
        
        if postamble != POSTAMBLE:
            raise ValueError('Bad response (POST)')
            
        # print(data.hex())
        cmd_id = b2i(payload[:2])
        data_len = b2i(payload[2:4])
        data = payload[4:4+data_len]

        return (cmd_id, data)


def main(port):
    with UVK5(port) as s:
        resp_ver = s.cmd(CMD_VERSION_REQ)
        cmd_resp(*resp_ver)
        size = 16*8
        for i in range(int(0xc80/size)):
            offset = 0x0F50 + i*size
            print('0x%x 0x%x' % (offset, size))
            resp_cfg = s.read_mem(offset, size)
            cmd_resp(*resp_cfg)
        

if __name__ == '__main__':
    main(argv[1])
