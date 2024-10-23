import asyncio
import websockets
import cv2
import numpy as np
import time

# Initialize variables for FPS calculation
fps = 0
start_time = time.time()
frame_count = 0

async def read_frames():
    global fps, start_time, frame_count
    uri = "wss://rgs.bansheeuav.tech:3000/read_frames"  # Replace with your server address
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server for reading frames")
        while True:
            frame_data = await websocket.recv()
            
            array = np.frombuffer(frame_data, dtype=np.uint8)
            
            frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
            
            # Increment frame count
            frame_count += 1

            # Calculate elapsed time
            elapsed_time = time.time() - start_time

            # Calculate FPS every second
            if elapsed_time >= 1:
                # Calculate FPS
                fps = frame_count / elapsed_time

                # Reset variables
                start_time = time.time()
                frame_count = 0

            # Display received video frame
            if frame is not None:
                # Display FPS on the frame
                cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Display the frame
                cv2.imshow("RECEIVING VIDEO", frame)
            else:
                print('Failed to decode frame')

            # Exit the live video stream
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

    cv2.destroyAllWindows()  # Close OpenCV windows when the loop ends

asyncio.run(read_frames())