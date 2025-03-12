from asyncio import *
import serial
import asyncio
import serial.tools.list_ports


async def connect_printer(port, bps_rate):
    try:
        printer = serial.Serial(port, bps_rate)
        print("[INFO] Connection succeed")
        return printer
    except Exception as e:
        print(f"[ERROR] {e}")


async def send_command(printer, command):
    pass


if __name__ == '__main__':
    asyncio.run(connect_printer(port="COM3", bps_rate=115200))