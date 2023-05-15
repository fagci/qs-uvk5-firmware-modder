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


def xor(var):
    return bytes(a ^ b for a, b in zip(var, cycle(KEY)))


def make_16byte_version(version):
    return bytes([ord(c) for c in version] + [0] * (16 - len(version)))


def decrypt(data):
    decr = xor(data)
    
    v = decr[V_OFFSET:V_OFFSET+V_LEN]
    decr_data = decr[:-CRC_LEN]

    eprint('version:', v)

    return decr_data


def encrypt(data, version='2.01.26'):
    v = make_16byte_version(version)
    eprint('version:', v)

    data = data[:V_OFFSET] + v + data[V_OFFSET+V_LEN:]
    encoded = xor(data)
    checksum = crc_hqx(encoded, 0).to_bytes(2, byteorder='little')

    return encoded + checksum
