import cv2
import mediapipe as mp
import asyncio
import websockets
import json

selected_client = "pc6-211"  # пример

async def send_mouse(x, y):
    address = "ws://localhost:3000"
    async with websockets.connect(address) as ws:
        await ws.send(json.dumps({"id": "control"}))
        payload = {"to": selected_client, "type": "python", "cmd": f"""
import ctypes
ctypes.windll.user32.SetCursorPos({x}, {y})
"""}
        await ws.send(json.dumps(payload))

# Настройка Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
cap = cv2.VideoCapture(0)

screen_width = 1920
screen_height = 1080

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # берем координату кончика указательного пальца
            x_norm = hand_landmarks.landmark[8].x  # нормированные 0..1
            y_norm = hand_landmarks.landmark[8].y
            x = int(x_norm * screen_width)
            y = int(y_norm * screen_height)
            # отправляем координаты на клиента
            asyncio.run(send_mouse(x, y))
    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
