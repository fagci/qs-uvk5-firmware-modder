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
    decrypted = xor(data)
    eprint('version:', decrypted[V_OFFSET:V_OFFSET+V_LEN])
    return decrypted[:-CRC_LEN]


def encrypt(data):
    encrypted = xor(data)
    checksum = crc_hqx(encrypted, 0).to_bytes(2, byteorder='little')
    return encrypted + checksum
