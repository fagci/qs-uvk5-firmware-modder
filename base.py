from itertools import cycle
from pathlib import Path
from sys import stderr

from crc import *

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
    crc_dec = decr[-CRC_LEN:]
    crc_enc = data[-CRC_LEN:]

    eprint('version:', v)
    eprint_crc(crc_dec)
    eprint_crc(crc_enc)

    crc1_test = crc_dec[0]*crc_dec[1]
    crc2_test = crc_enc[0]*crc_enc[1]

    for crc_f in [crc16_xmodem, crc16_buypass, crc16_ccitt_false, crc16_modbus]:
        for d in [data[:-CRC_LEN], decr_data, decr_data[:V_OFFSET]+decr_data[V_OFFSET+V_LEN:-CRC_LEN], data[:V_OFFSET]+data[V_OFFSET+V_LEN:-CRC_LEN]]:
            crc_try = crc_f(d)
            eprint('try:', crc_try)
            if crc_try == crc1_test:
                eprint('BINGO: crc1_test', crc_try)
                break
            if crc_try == crc2_test:
                eprint('BINGO: crc2_test', crc_try)
                break

    return decr_data
