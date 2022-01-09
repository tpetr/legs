import enum
from collections import namedtuple

ACCEL_MULTIPLIER = 16 * 9.8 / 32768
ANG_VEC_MULTIPLIER = 2000 / 32768
ANGLE_MULTIPLIER = 180 / 32768


Packet = namedtuple("Packet", "timestamp ax ay az wx wy wz roll pitch yaw")


class ReturnRate(enum.IntEnum):
    RATE_TENTH_HZ = 1
    RATE_HALF_HZ = 2
    RATE_1HZ = 3
    RATE_2HZ = 4
    RATE_5HZ = 5
    RATE_10HZ = 6
    RATE_20HZ = 7
    RATE_50HZ = 8


class SaveSetting(enum.IntEnum):
    SAVE_CURRENT_CONFIG = 0
    RESTORE_DEFAULT_CONFIG = 1


class CalibrationMode(enum.IntEnum):
    ACCEL = 1
    MAG = 7
    QUIT = 0


class Register(enum.IntEnum):
    SAVE = 0x00
    CALSW = 0x01
    # 0x2 RSV
    RATE = 0x03
    BAUD = 0x04
    AXOFFSET = 0x05
    AYOFFSET = 0x06
    AZOFFSET = 0x07
    GXOFFSET = 0x08
    GYOFFSET = 0x09
    GZOFFSET = 0x0A
    HXOFFSET = 0x0B
    HYOFFSET = 0x0C
    HZOFFSET = 0x0D
    D0MODE = 0x0E
    D1MODE = 0x0F
    D2MODE = 0x10
    D3MODE = 0x11
    # 0x12 - 0x2f RSV
    REGISTER = 0x27

    YYMM = 0x30
    DDHH = 0x31
    MMSS = 0x32
    MS = 0x33
    AX = 0x34
    AY = 0x35
    AZ = 0x36
    GX = 0x37
    GY = 0x38
    GZ = 0x39
    HX = 0x3A
    HY = 0x3B
    HZ = 0x3C
    ROLL = 0x3D
    PITCH = 0x3E
    YAW = 0x3F
    TEMP = 0x40
    D0STATUS = 0x41
    D1STATUS = 0x42
    D2STATUS = 0x43
    D3STATUS = 0x44
    # 0x49-0x50 RSV
    Q0 = 0x51
    Q1 = 0x52
    Q2 = 0x53
    Q3 = 0x54
