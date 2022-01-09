import asyncio
import sys
import psycopg2
import os

from client import Packet, Client, ReturnRate


async def main():
    with psycopg2.connect(os.environ["DSN"]) as conn:
        print("Connected")
        conn.autocommit = True
        with conn.cursor() as cursor:
            async with await Client.discover() as c:
                await c.set_return_rate(ReturnRate.RATE_1HZ)
                while True:
                    packet = await c.wait_for_packet()
                    cursor.execute(
                        """INSERT INTO legs(time, ax, ay, az, wx, wy, wz, roll, pitch, yaw) VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        packet.ax,
                        packet.ay,
                        packet.az,
                        packet.wx,
                        packet.wy,
                        packet.wz,
                        packet.roll,
                        packet.pitch,
                        packet.yaw,
                    )


asyncio.run(main())
