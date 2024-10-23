import asyncio
import websockets
import cv2
import ssl

async def send_frames():
    uri = "wss://rgs.bansheeuav.tech:3000/sending_frames"  # WebSocket endpoint for sending frames
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)  # Create SSL context with TLS
    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        print("Connected to WebSocket server for sending frames")
        cap = cv2.VideoCapture(0)
        while True:
            try:
                ret, frame = cap.read()
                if not ret: 
                    break
                frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
                await websocket.send(frame_bytes)
                print("Sent frame")
            except Exception as e:
                print(e)
                break

asyncio.run(send_frames())