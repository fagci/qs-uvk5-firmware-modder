from binascii import crc_hqx as crc16
from itertools import cycle
from sys import stderr
from pathlib import Path

# Structure of pre-encoded payload
# 8196 | 16      | ...  | 2   |
# data | version | data | crc |

LIB_DIR = Path(__file__).parent
DATA_DIR = LIB_DIR / '..' / 'data'
KEY = (DATA_DIR / 'key.bin').read_bytes()

V_START = 8192
V_END = V_START + 16
CRC_LEN = 2

def eprint(*args, **kwargs):
    print(*args, **kwargs, file=stderr)


def xor(var):
    return bytes(a ^ b for a, b in zip(var, cycle(KEY)))


def make_16byte_version(version):
    return bytes([ord(c) for c in version] + [0] * (16 - len(version)))


def decrypt(data):
    decrypted = xor(data)
    version = decrypted[V_START:V_END].decode().rstrip('\x00')
    return (decrypted[:V_START] + decrypted[V_END:-CRC_LEN], version)


def encrypt(data, version='2.01.26'):
    v = make_16byte_version(version)
    encrypted = xor(data[:V_START] + v + data[V_START:])
    checksum = crc16(encrypted, 0).to_bytes(2, 'little')
    return encrypted + checksum

