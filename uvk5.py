#!/usr/bin/env python3

from binascii import crc_hqx
from itertools import cycle
import os
import struct
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


def xor_fw(var):
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


def is_decrypted(data):
    return data[:4] == b'\x88\x13\x00\x20' or data[:4] == b'\x88\x11\x00\x20'


def search_for_version(data):
    pre = bytes.fromhex('2135D5401303E980')
    plen = len(pre)
    for i in range(len(data)-plen):
        if data[i:i+plen] == pre:
            return data[i+plen:i+plen+16].decode(errors='ignore').rstrip('\x00').split('_')[1]
    return 'unknown'



def decrypt(data):
    decrypted = xor_fw(data)
    version = decrypted[V_START:V_END].decode().rstrip('\x00')
    return (decrypted[:V_START] + decrypted[V_END:-CRC_LEN], version)


def encrypt(data, version='2.01.26'):
    v = make_16byte_version(version)
    encrypted = xor_fw(data[:V_START] + v + data[V_START:])
    checksum = crc16(encrypted)
    return encrypted + checksum


class Firmware(bytearray):
    @classmethod
    def load(cls, path):
        data = Path(path).read_bytes()
        if is_decrypted(data):
            version = search_for_version(data)
        else:
            data, version = decrypt(data)

        return globals().get(f'Firmware_{version.replace(".", "_")}', cls)(data, version)

    def __init__(self, data, version) -> None:
        super().__init__(data)
        self.version = version


    def compare(self, fw):
        a = None
        la = len(self)
        lb = len(fw)
        changes = {}
        for i in range(min(la, lb)):
            differ = self[i] != fw[i]
            if not differ:
                a = None
                continue

            if not a:
                a = '0x%x' % i
                changes[a] = [bytearray(), bytearray()]

            changes[a][0].append(self[i])
            changes[a][1].append(fw[i])


        for addr, ch in changes.items():
            print(f'{addr}:', ch[0].hex(), ch[1].hex())


    def search(self, q):

        search_for_len = len(q)

        for i in range(len(self)):
            if self[i:i+search_for_len] == q:
                print(f'[{i}]: {self[i:i+32]}')



    def patch_single(self, addr, new_value, size=4):
        old_bytes = self[addr:addr+size]
        old_value = int.from_bytes(old_bytes, 'little')
        new_bytes = int(new_value).to_bytes(size, 'little')
        self[addr:addr+size] = new_bytes


    def write(self, path=None):
        encrypted = encrypt(self, self.version)

        if path:
            pass
        else:
            os.write(1, encrypted)


    def write_raw(self, path=None):
        if path:
            pass
        else:
            os.write(1, self)


class FirmwareModifiable(Firmware):
    def apply_mods(self, mod_names):
        for mod in mod_names:
            getattr(self, f'mod_{mod}')()

    def get_available_mods(self):
        for func in dir(self):
            if callable(getattr(self, func)) and func.startswith('mod_'):
                yield func[4:]

    def mod_unlimit_rx(self):
        self.patch_single(self.ADR_BANDS[0][0], 18_000_000//10)
        self.patch_single(self.ADR_BANDS[6][1], 1_300_000_000//10)
        self.patch_single(self.ADR_LIMITS[0], 18_000_000//10)
        self.patch_single(self.ADR_LIMITS[1], 1_300_000_000//10)

    def mod_unlimit_tx(self):
        self.patch_single(self.ADR_TX_CHECK, b'\x5d\xe0', 2)


class Firmware_2_01_17(FirmwareModifiable):
    ADR_BANDS = [
        [0xEAE4,0xEB00],
        [0xEAE8,0xEB04],
        [0xEAEC,0xEB08],
        [0xEAF0,0xEB0C],
        [0xEAF4,0xEB10],
        [0xEAF8,0xEB14],
        [0xEAFC,0xEB18],
    ]
    ADR_LIMITS = [0x1AF0, 0x1AF4]


class Firmware_2_01_26(FirmwareModifiable):
    ADR_BANDS = [
        [0xE074, 0xE090],
        [0xE078, 0xE094],
        [0xE07C, 0xE098],
        [0xE080, 0xE09C],
        [0xE084, 0xE0A0],
        [0xE088, 0xE0A4],
        [0xE08C, 0xE0A8],
    ]
    ADR_LIMITS = [0x150C, 0x1510]
    ADR_TX_CHECK = 0x180E



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

    def send_firmware(self, fw:Firmware):
        for block, data in enumerate(chunk(fw, UVK5.BLOCK_SIZE)):
            offset = block * UVK5.BLOCK_SIZE
            self.write_fw(offset, data)
        exit(128)

    def write_fw(self, offset, data):
        eprint('FW write not implemented yet', offset, len(data))

    def get_version(self):
        return self.cmd(UVK5.CMD_VERSION_REQ)[1][:10].decode().rstrip('\x00')

    def read_mem(self, offset, size):
        return self.cmd(UVK5.CMD_SETTINGS_REQ, i2b32(offset) + i2b16(size))

    def write_patch(self):
        from patch import PATCH
        print(len(PATCH))
        def divide_chunks(l, n): 
            for i in range(0, len(l), n):  
                yield l[i:i + n]
        offset = 0
        for chunk in divide_chunks(PATCH,8):
            print(f"Write at {offset}...")
            self.cmdw(0x061D, offset, bytes(chunk))
            offset += len(chunk)

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
            raise ValueError('Bad response (POST)', postamble, payload, payload_len)
            
        # print(data.hex())
        cmd_id = b2i(payload[:2])
        data_len = b2i(payload[2:4])
        data = payload[4:4+data_len]

        return (cmd_id, data)

    def cmdw(self, id, address,payload):
        self.write(self._cmd_make_reqw(id, address, payload))
        preamble = self.read(2)

        if preamble != UVK5.PREAMBLE:
            raise ValueError('Bad response (PRE)', preamble)

        payload_len = b2i(self.read(2)) + 2 # CRC len
        payload = xor_comm(self.read(payload_len))

        # crc = payload[-2:]
        postamble = self.read(2)
        
        if postamble != UVK5.POSTAMBLE:
            raise ValueError('Bad response (POST)', postamble, payload, payload_len)
            
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

    def read_eeprom(self, offset, size):
        size = int(size) if size else UVK5.BLOCK_SIZE
        data = self.read_mem(offset, size)
        print(data[1])


    def _cmd_make_req(self, cmd_id, body=b''):
        data = body + self.timestamp
        payload = i2b16(cmd_id) + len16(data) + data
        encoded_payload = xor_comm(payload + crc16(payload))

        return UVK5.PREAMBLE + len16(payload) + encoded_payload + UVK5.POSTAMBLE

    def _cmd_make_reqw(self, cmd_id, address, payload):
        payload = i2b16(cmd_id) + struct.pack('<HHH',len(payload)+8, address, len(payload)) + self.timestamp + payload
        encoded_payload = xor_comm(payload + crc16(payload))

        return UVK5.PREAMBLE + len16(payload) + encoded_payload + UVK5.POSTAMBLE
        


if __name__ == '__main__':
    if len(argv) < 3:
        eprint(f'Usage: {argv[0]} <port> <command:(channels|version)> [args]')
        exit(255)

    port = argv[1]
    cmd = argv[2]
    args = argv[3:]
    for i in range(len(args)):
        if args[i][:2] == '0x':
            args[i] = int(args[i][2:], 16)

    with UVK5(port) as s:
        version = s.get_version()
        if cmd == 'version':
            print('FW Version:', version)
            exit(0)

        res = getattr(s, cmd)(*args)
        if res:
            print(res)

