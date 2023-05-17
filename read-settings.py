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

def crc16(data):
    return crc_hqx(data, 0).to_bytes(2,'little')


def len16(data):
    return int.to_bytes(len(data), 2, byteorder='little')


def xor(var):
    return bytes(a ^ b for a, b in zip(var, cycle(KEY)))
    

def timestamp32():
    return int(time()).to_bytes(4, 'little')


def cmd16(cmd_id):
    return cmd_id.to_bytes(2,'little')


def cmd_req(cmd_id, body=b''):
    data = body + timestamp32()
    payload = cmd16(cmd_id) + len16(data) + data
    encoded_payload = xor(payload + crc16(payload))

    return PREAMBLE + len16(payload) + encoded_payload + POSTAMBLE


def cmd_resp(cmd_id, data):
    if cmd_id == CMD_VERSION_RES:
        print(data[:10].decode())


def main(port):
    cmd = cmd_req(CMD_VERSION_REQ)
    with Serial(port, 38400, timeout=5) as s:
        s.write(cmd)
        preamble = s.read(2)

        if preamble != PREAMBLE:
            print('Bad response')
            exit(128)

        payload_len = int.from_bytes(s.read(2), 'little')
        data = xor(s.read(payload_len))
        # print(data.hex())
        cmd_id = int.from_bytes(data[:2], 'little')
        data_len = int.from_bytes(data[2:4], 'little')
        cmd_resp(cmd_id, data[4:4+data_len])
        

if __name__ == '__main__':
    main(argv[1])
