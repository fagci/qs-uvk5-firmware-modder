#!/usr/bin/env python3

from binascii import crc_hqx
from itertools import cycle
from sys import argv
from time import time

from serial import Serial

KEY = bytes.fromhex('166c14e62e910d402135d5401303e980')
PREAMBLE = b'\xab\xcd'
POSTAMBLE = b'\xdc\xba'

CMD_VERSION_REQ = 0x0514
CMD_VERSION_RES = 0x0515

CMD_SETTINGS_REQ = 0x051B
CMD_SETTINGS_RES = 0x051C


def xor(var):
    return bytes(a ^ b for a, b in zip(var, cycle(KEY)))
    

def timestamp32():
    return int(time()).to_bytes(4, 'little')


def i2b16(cmd_id):
    return cmd_id.to_bytes(2,'little')


def b2i(data):
    return int.from_bytes(data, 'little')


def len16(data):
    return i2b16(len(data))


def crc16(data):
    return i2b16(crc_hqx(data, 0))


def cmd_make_req(cmd_id, body=b''):
    data = body + timestamp32()
    payload = i2b16(cmd_id) + len16(data) + data
    encoded_payload = xor(payload + crc16(payload))

    return PREAMBLE + len16(payload) + encoded_payload + POSTAMBLE


def cmd_resp(cmd_id, data):
    # print('%x'%cmd_id)
    if cmd_id == CMD_VERSION_RES:
        print('FW version:', data[:10].decode())
        return

    if cmd_id == CMD_SETTINGS_RES:
        print('Channels:')
        channel_names = data[4:]
        for i in range(len(channel_names)//16):
            print(channel_names[i*16:(i+1)*16].decode())
        return


class UVK5(Serial):
    def __init__(self, port: str | None = None) -> None:
        super().__init__(port, 38400, timeout=5)


    def cmd(self, id, body = b''):
        self.write(cmd_make_req(id, body))
        preamble = self.read(2)

        if preamble != PREAMBLE:
            print('Bad response (PRE)')
            exit(128)

        payload_len = b2i(self.read(2))
        data = xor(self.read(payload_len))

        self.read(2)
        postamble = self.read(2)
        
        if postamble != POSTAMBLE:
            print('Bad response (POST)')
            exit(128)
            
        # print(data.hex())
        cmd_id = b2i(data[:2])
        data_len = b2i(data[2:4])

        return (cmd_id, data[4:4+data_len])


def main(port):
    with UVK5(port) as s:
        resp_ver = s.cmd(CMD_VERSION_REQ)
        cmd_resp(*resp_ver)

        resp_cfg = s.cmd(CMD_SETTINGS_REQ, i2b16(0x0F50) + i2b16(0x0C80))
        cmd_resp(*resp_cfg)
        

if __name__ == '__main__':
    main(argv[1])
