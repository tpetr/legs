import asyncio
import csv
import sys

from client import Packet, Client, ReturnRate


class DeltaOfDeltas:
    def __init__(self):
        self.last_value = None
        self.last_delta = None

    def update(self, value):
        if not self.last_value:
            self.last_value = (0,) * len(value)
            self.last_delta = value
            return value
        delta = (a - b for a, b in zip(value, self.last_value))
        delta_of_delta = (a - b for a, b in zip(delta, self.last_delta))
        self.last_value = value
        self.last_delta = delta
        return delta_of_delta


async def main():
    dd = DeltaOfDeltas()

    writer = csv.writer(sys.stdout)
    writer.writerow(Packet._fields)
    async with await Client.discover() as c:
        await c.set_return_rate(ReturnRate.RATE_1HZ)
        while True:
            packet = await c.wait_for_packet()
            writer.writerow(dd.update(packet))


asyncio.run(main())
