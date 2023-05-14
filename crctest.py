
# CRC-16/CCITT-FALSE
def crc16_ccitt_false(data : bytearray):
    offset = 0
    length = len(data)
    if data is None or offset < 0 or offset > len(data)- 1 and offset+length > len(data):
        return 0
    crc = 0xFFFF
    for i in range(0, length):
        crc ^= data[offset + i] << 8
        for j in range(0,8):
            if (crc & 0x8000) > 0:
                crc =(crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF

# CRC-16/BUYPASS, CRC-16-ANSI, CRC-16-IBM
def crc16_buypass(data: bytes):
    xor_in = 0x0000  # initial value
    xor_out = 0x0000  # final XOR value
    poly = 0x8005  # generator polinom (normal form)
    reg = xor_in
    for octet in data:
        # reflect in
        for i in range(8):
            topbit = reg & 0x8000
            if octet & (0x80 >> i):
                topbit ^= 0x8000
            reg <<= 1
            if topbit:
                reg ^= poly
        reg &= 0xFFFF
        # reflect out
    return reg ^ xor_out

# https://docs.python.org/3/library/binascii.html
import binascii
def crc16_xmodem(data: bytes):
  return binascii.crc_hqx(data, 0)

def crc16_modbus(data : bytearray):
    offset = 0
    length = len(data)
    if data is None or offset < 0 or offset > len(data) - 1 and offset + length > len(data):
        return 0
    crc = 0xFFFF
    for i in range(length):
        crc ^= data[offset + i]
        for j in range(8):
            if ((crc & 0x1) == 1):
                crc = int((crc / 2)) ^ 40961
            else:
                crc = int(crc / 2)
    return crc & 0xFFFF



