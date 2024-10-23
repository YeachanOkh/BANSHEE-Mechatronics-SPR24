import asyncio
import websockets
import cv2
import numpy as np
from realsense_depth import DepthCamera
import ssl

async def send_frames():
    uri = "wss://rgs.bansheeuav.tech:3000/sending_frames"  # WebSocket endpoint for sending frames
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)  # Create SSL context with TLS
    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        print("Connected to WebSocket server for sending frames")
        video_capture = DepthCamera()  # Use 0 for webcam, or file path for a video file
        while True:
            try:
                ret, depth_frame, color_frame = video_capture.get_frame()
                if not ret: 
                    break

                # Encode and send depth frame with header
                depth_frame_bytes = cv2.imencode('.png', depth_frame)[1].tobytes()
                await websocket.send(b'DEPTH_FRAME' + depth_frame_bytes)

                # Encode and send color frame with header
                color_frame_bytes = cv2.imencode('.jpg', color_frame)[1].tobytes()
                await websocket.send(b'COLOR_FRAME' + color_frame_bytes)

                print('Sending frames')
            except Exception as e:
                print(e)
                break
            key = cv2.waitKey(1)
            if key == 27:
                break

asyncio.run(send_frames())
