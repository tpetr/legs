import asyncio
import enum
import struct
import time
from typing import Tuple, Any

from bleak import BleakClient, BleakScanner

from models import (
    Register,
    ReturnRate,
    Packet,
    SaveSetting,
    CalibrationMode,
    ACCEL_MULTIPLIER,
    ANG_VEC_MULTIPLIER,
    ANGLE_MULTIPLIER,
)

SERVICE_UUID = "0000FFE5-0000-1000-8000-00805F9A34FB"
READ_UUID = "0000FFE4-0000-1000-8000-00805F9A34FB"
WRITE_UUID = "0000FFE9-0000-1000-8000-00805F9A34FB"

HEADER_BYTES = b"\xFF\xAA"


def unpack_packet(data) -> Packet:
    ax, ay, az, avx, avy, avz, x, y, z = struct.unpack("<hhhhhhhhh", data[2:])
    return Packet(
        time.time_ns(),
        ax * ACCEL_MULTIPLIER,
        ay * ACCEL_MULTIPLIER,
        az * ACCEL_MULTIPLIER,
        avx * ANG_VEC_MULTIPLIER,
        avy * ANG_VEC_MULTIPLIER,
        avz * ANG_VEC_MULTIPLIER,
        x * ANGLE_MULTIPLIER,
        y * ANGLE_MULTIPLIER,
        z * ANGLE_MULTIPLIER,
    )


class Client:
    @classmethod
    async def discover(cls, timeout=5):
        async with BleakScanner(service_uuids=[SERVICE_UUID]) as scanner:
            for i in range(timeout):
                if scanner.discovered_devices:
                    return cls(scanner.discovered_devices[0])
                await asyncio.sleep(1)
        if not scanner.discovered_devices:
            raise Exception("Device not found")

    def __init__(self, device):
        self.client = BleakClient(device)
        self.command_lock = asyncio.Lock()
        self.register_event = asyncio.Event()
        self.packet_event = asyncio.Event()
        self.last_register = None
        self.last_packet = None
        self.last_return_rate = None

    async def handle_data(self, handle, data):
        match data[0:2]:
            case b"\x55\x71":
                self.last_register = data
                self.register_event.set()
            case b"\x55\x61":
                self.last_packet = unpack_packet(data)
                self.packet_event.set()
            case _:
                pass  # TODO: log

    async def __aenter__(self):
        await self.client.connect()
        await self.client.start_notify(READ_UUID, self.handle_data)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.stop_notify(READ_UUID)
        await self.client.disconnect()

    async def wait_for_packet(self) -> Packet:
        await self.packet_event.wait()
        try:
            return self.last_packet
        finally:
            self.packet_event.clear()

    async def write_register(self, register: Register, value: enum.IntEnum):
        await self.client.write_gatt_char(
            WRITE_UUID,
            HEADER_BYTES + register.to_bytes(1, "little") + value.to_bytes(2, "little"),
        )

    async def read_register_value(self, register: Register) -> bytes:
        async with self.command_lock:
            await self.write_register(Register.REGISTER, register)
            await self.register_event.wait()
            self.register_event.clear()
            return self.last_register

    async def read_magnetic_field(self) -> Tuple[Any]:
        data = await self.read_register_value(Register.HX)
        return struct.unpack("<hhh", data[4:])

    async def read_quaternion(self) -> Tuple[Any]:
        data = await self.read_register_value(Register.Q0)
        return tuple(value / 32768 for value in struct.unpack("<hhhh", data[4:]))

    async def read_temperature(self) -> float:
        data = await self.read_register_value(Register.TEMP)
        (value,) = struct.unpack("<h", data[4:])
        return value * 0.01

    async def set_return_rate(self, rate: ReturnRate):
        self.last_return_rate = rate
        await self.write_register(Register.RATE, rate)

    async def save_configuration(self, setting: SaveSetting):
        await self.write_register(Register.SAVE, setting)

    async def calibrate(self, mode: CalibrationMode):
        await self.write_register(Register.CALSW, mode)
