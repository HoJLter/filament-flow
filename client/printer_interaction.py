import subprocess

import aiohttp
import asyncpg
import asyncio
import serial
import time

database_config = {
    "host": "optiprt-pgsql-sojlter.db-msk0.amvera.tech",
    "database": "optiprt-database",
    "user": "SoJLter",
    "password": "4mil4"
}
token = "7637207985:AAErMgsCNA11pGuYzO4Qo5oSI3rucfRs3fs"


# oleg
async def stl_main():
    connection: asyncpg.Connection = await asyncpg.connect(**database_config)
    while True:
        response = await connection.fetchrow(
            "SELECT id_tg_file "
            "FROM order_info "
            "INNER JOIN orders ON orders.id_order = order_info.id_order "
            "WHERE status = 'ОДОБРЕН';"
        )

        if response:
            file_id = response[0]
            print(file_id)
            #     await connection.fetchrow(
            #         "UPDATE orders "
            #         "SET status = 'ЗАВЕРШЕННЫЙ'"
            #     )
            await download_stl(file_id)
        await asyncio.sleep(10)


def get_gcode(stl_path, output_path):
    kisslicer_path = r"KISSlicer\KISSlicer.exe"

    command = [
        kisslicer_path,
        "-o", output_path,
        stl_path
    ]
    try:

        result = subprocess.run(command, capture_output=True,
                                text=True, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(e)
        return False


async def start_printing(gcode_path):
    # reads the gcode file
    gcodeFile = open(gcode_path, 'r')
    gcode = gcodeFile.readlines()

    printer = serial.Serial("COM3", 115200)

    for line in gcode:
        response = ''
        line = line.split(";")[0]
        if (line != "" and line != "\n"):
            print("line: " + line)
            printer.write(str.encode(line + '\n'))
            while response.count("ok") == 0:
                # waits for response
                while printer.in_waiting == 0:
                    time.sleep(0.5)
                response = ''
                while printer.in_waiting > 0:
                    response += str(printer.readline())
                print(response)


async def download_stl(file_id):
    async with aiohttp.ClientSession() as session:
        url = f'https://api.telegram.org/bot{token}/getFile?file_id={file_id}'
        async with session.get(url) as response:
            if response.status == 200:
                file_info = await response.json()
                file_path = file_info['result']['file_path']

                file_url = f'https://api.telegram.org/file/bot{token}/{file_path}'
                async with session.get(file_url) as file_response:
                    if file_response.status == 200:
                        # Сохраняем файл на локальный компьютер
                        with open('data/model.stl', 'wb') as f:
                            f.write(await file_response.read())
                        print("Файл успешно скачан!")
                    else:
                        print("Ошибка при скачивании файла:")
                get_gcode("data/model.stl", "data/")
                await start_printing("data/.gcode")


if __name__ == '__main__':
    asyncio.run(stl_main())