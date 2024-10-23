import asyncio
import websockets
import cv2
import time 


async def send_frames():
    uri = "wss://rgs.bansheeuav.tech:3000/sending_frames"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server for sending frames")
        cap = cv2.VideoCapture(0)
        frame_rate = 60
        prev = 0
        while True:
            try:
                #ret, frame = cap.read()
                #while capturing:
                time_elapsed = time.time() - prev
                ret, frame = cap.read()
                if time_elapsed > 1./frame_rate:
                    prev = time.time()
                #ret, frame = cap.read()
                if not ret: 
                    break
                frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
                ret = await websocket.send(frame_bytes)
                print("Sent frame")
            except Exception as e:
                print(e)
                break

asyncio.run(send_frames())