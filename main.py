import asyncio
import sys
import pg8000
import os
import ssl
from collections import deque

from client import Packet, Client, ReturnRate
from models import DeviceNotFound


async def data_writer(queue):
    ssl_context = ssl.SSLContext()
    ssl_context.verify_mode = ssl.CERT_NONE  # TODO: fix this
    with pg8000.dbapi.connect(
        user=os.environ["PG_USER"],
        host=os.environ["PG_HOST"],
        database=os.environ["PG_DATABASE"],
        port=int(os.environ["PG_PORT"]),
        password=os.environ["PG_PASSWORD"],
        ssl_context=ssl_context,
    ) as conn:
        print("Connected to DB")
        conn.autocommit = True
        cursor = conn.cursor()
        while True:
            await asyncio.sleep(1)
            data = []
            while True:
                try:
                    data.append(queue.get_nowait())
                except asyncio.QueueEmpty:
                    break
            if data:
                cursor.executemany(
                    """INSERT INTO legs(time, ax, ay, az, wx, wy, wz, roll, pitch, yaw) VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    data,
                )


async def data_collector(queue):
    while True:
        try:
            async with await Client.discover() as c:
                await c.set_return_rate(ReturnRate.RATE_10HZ)
                print("Receiving data...")
                while True:
                    queue.put_nowait(await c.wait_for_packet())
        except DeviceNotFound:
            print("Device not found, retrying in 5 sec")
            await asyncio.sleep(5)


async def main():
    queue = asyncio.Queue()

    await asyncio.gather(data_collector(queue), data_writer(queue))


asyncio.run(main())
