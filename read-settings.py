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
        self.write(UVK5.cmd_make_req(id, body))
        preamble = self.read(2)

        if preamble != PREAMBLE:
            print('Bad response (PRE)')
            exit(128)

        payload_len = int.from_bytes(self.read(2), 'little')
        data = UVK5.xor(self.read(payload_len))

        self.read(2)
        postamble = self.read(2)
        
        if postamble != POSTAMBLE:
            print('Bad response (POST)')
            exit(128)
            
        # print(data.hex())
        cmd_id = int.from_bytes(data[:2], 'little')
        data_len = int.from_bytes(data[2:4], 'little')

        return (cmd_id, data[4:4+data_len])


    @classmethod
    def cmd_make_req(cls, cmd_id, body=b''):
        data = body + UVK5.timestamp32()
        payload = UVK5.cmd16(cmd_id) + UVK5.len16(data) + data
        encoded_payload = UVK5.xor(payload + UVK5.crc16(payload))

        return PREAMBLE + UVK5.len16(payload) + encoded_payload + POSTAMBLE

    @classmethod
    def crc16(cls, data):
        return crc_hqx(data, 0).to_bytes(2,'little')


    @classmethod
    def len16(cls, data):
        return int.to_bytes(len(data), 2, byteorder='little')


    @classmethod
    def xor(cls, var):
        return bytes(a ^ b for a, b in zip(var, cycle(KEY)))
        

    @classmethod
    def timestamp32(cls):
        return int(time()).to_bytes(4, 'little')


    @classmethod
    def cmd16(cls, cmd_id):
        return cmd_id.to_bytes(2,'little')


def main(port):
    with UVK5(port) as s:
        resp_ver = s.cmd(CMD_VERSION_REQ)
        cmd_resp(*resp_ver)

        resp_cfg = s.cmd(CMD_SETTINGS_REQ, 0x0F50.to_bytes(2, 'little') + 0x0C80.to_bytes(2, 'little'))
        cmd_resp(*resp_cfg)
        

if __name__ == '__main__':
    main(argv[1])
