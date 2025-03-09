import time

import subprocess
import pyautogui


async def kisslicer_run():
    kisslicer_path = ("model_processing/KISSlicer/KISSlicer64.exe")
    process = subprocess.Popen([kisslicer_path, 'test_model.stl']) #Запуск KiSSLicer

    time.sleep(2)
    pyautogui.hotkey('ctrl', 's')
    time.sleep(15)
    pyautogui.hotkey('ctrl', 's')
    time.sleep(3)
    pyautogui.hotkey('enter')
    process.kill()


async def params_get(nozzle_temp=None):
    pass