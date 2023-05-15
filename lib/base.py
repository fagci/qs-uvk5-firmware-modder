from itertools import cycle
from pathlib import Path
from sys import stderr
from binascii import crc_hqx

# Structure of pre-encoded payload
# 8196 | 16      | ...  | 2   |
# data | version | data | crc |

KEY = Path('./key.bin').read_bytes()

V_OFFSET = 8192
V_LEN = 16
CRC_LEN = 2

def eprint(*args, **kwargs):
    print(*args, **kwargs, file=stderr)


def xor(var, key):
    return bytes(a ^ b for a, b in zip(var, cycle(key)))


def eprint_crc(crc):
    eprint('crc:', ['0x%02x' % x for x in crc], f'{crc[0]*crc[1]}')


def make_16byte_version(version):
    return bytes([ord(c) for c in version] + [0] * (16 - len(version)))


def decrypt(data):
    decr = xor(data, KEY)
    
    v = decr[V_OFFSET:V_OFFSET+V_LEN]
    decr_data = decr[:-CRC_LEN]
    crc = decr[-CRC_LEN:]

    eprint('version:', v)
    eprint_crc(crc)

    return decr_data


def encrypt(data, version='2.01.19'):
    v = make_16byte_version(version)
    data = data[:V_OFFSET] + v + data[V_OFFSET+V_LEN:]
    crc = b'\xd9\xab' # here will be some crc
    
    eprint('version:', v)
    eprint_crc(crc)

    return xor(data + crc, KEY)

def crctest(data):
    decr = xor(data, KEY)
    
    v = decr[V_OFFSET:V_OFFSET+V_LEN]
    decr_data = decr[:-CRC_LEN]

    eprint('version:', v)

    checksum = crc_hqx(data[:-CRC_LEN], 0)
    file_checksum = int.from_bytes(data[-CRC_LEN:], byteorder='little')
    print(f'Calculated checksum:', checksum)
    print(f'File checksum:', file_checksum)

    return decr_data
