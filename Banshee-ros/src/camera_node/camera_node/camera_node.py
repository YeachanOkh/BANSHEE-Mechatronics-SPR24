import rclpy
from rclpy.node import Node
import cv2
import numpy as np
import asyncio
import threading
import ssl
import websockets
from std_msgs.msg import String

class CameraNode(Node):
    def __init__(self):
        super().__init__("camera_node")
        self.x_values_equal = 0
        self.arucoID = None
        self.websocket = None
        
        self.subscription = self.create_subscription(
            String, 
            'arucoID', 
            self.subscriberNode, 
            10
        )
        
        # Start the camera thread
        self.camera_thread = threading.Thread(target=self.cameraRun)
        self.camera_thread.start()

        # Start the WebSocket thread
        self.websocket_thread = threading.Thread(target=self.start_websocket)
        self.websocket_thread.start()

        self.get_logger().info("Camera node initialized and WebSocket task started")

    def subscriberNode(self, msg):
        self.arucoID = int(msg.data)
        self.get_logger().info(f"Received Aruco ID: {self.arucoID}")

    def cameraRun(self):
        self.get_logger().info("Connected to WebSocket server for sending frames")

        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)  # Choose your desired dictionary
        detector_parameters = cv2.aruco.DetectorParameters()
        refine_parameters = cv2.aruco.RefineParameters()
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            exit()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame. Exiting ...")
                break
            # Get frame dimensions
            height, width, _ = frame.shape
            #set middle box height and weight
            box_size = 50
            box_x = int((width - box_size) / 2)
            box_y = int((height - box_size) / 2)

            # 4. Detect ArUco markers
            detector = cv2.aruco.ArucoDetector(aruco_dict, detector_parameters, refine_parameters)

            marker_corners, marker_ids, rejectedImgPoints = detector.detectMarkers(frame)

            middle_x = 0

            # 5. Draw detected markers on the frame and calculate overlap
            # check to see if ar marker is being recognized
            if marker_ids is not None:
                for ids, corners in zip(marker_ids, marker_corners):
                # Calculate the overlap between the middle box and ArUco marker detection box
                    middle_box = np.array([[box_x, box_y], [box_x + box_size, box_y + box_size]])
                    aruco_box = np.int32(corners[0])  # Convert corners to integer for calculations
                    if ids == self.arucoID:
                        corner1_x = aruco_box[0][0] # Top left x value
                        corner2_x = aruco_box[2][0] # Bottom right x value
                        middle_x = (corner1_x + corner2_x) / 2
                        distance = abs(middle_x - int(width / 2))

                        cv2.putText(frame, f"distance: {distance}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,1, (255, 255, 255), 2, cv2.LINE_AA)

                    intersection_area = cv2.contourArea(cv2.convexHull(np.concatenate([middle_box, aruco_box])))
                    union_area = box_size**2 + cv2.contourArea(cv2.convexHull(aruco_box)) - intersection_area
                    if union_area == 0:
                        union_area = 0.01
                    overlap_ratio = intersection_area / union_area

                    # Display the confidence level between 0 and 100
                    if overlap_ratio<=1 and overlap_ratio>0:
                        #if confidence level hits at least 98%
                        if overlap_ratio<=1 and overlap_ratio>=.98:
                            #turn on arm
                            armstart=True
                        # print(armstart)
                        #put text for ratio next to ar marker boxes
                        cv2.putText(frame, f"Overlap Ratio: {overlap_ratio:.2%}",(int(corners[0][:, 0].mean()), int(corners[0][:, 1].mean()) + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)     

                # Draw detected markers after calculating overlap
                cv2.aruco.drawDetectedMarkers(frame, marker_corners, marker_ids)

                # Draw the center box on the frame
                cv2.rectangle(frame, (box_x, box_y), (box_x + box_size, box_y + box_size), (0, 255, 0), 2)

            # Send frame over WebSocket (if connection is active)
            if self.websocket is not None:
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                asyncio.run(self.websocket.send(frame_bytes))  # Send frame bytes to WebSocket

            cv2.imshow("Camera live stream", frame)

            if cv2.waitKey(1) == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    async def websocket_handler(self):
        uri = "wss://rgs.bansheeuav.tech/ws"  # Replace with your WebSocket endpoint
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)

        async with websockets.connect(uri, ping_interval=30, ping_timeout=20, ssl=ssl_context) as websocket:
            self.websocket = websocket  # Set websocket attribute once connection is established
            self.get_logger().info("Connected to WebSocket server for sending frames")
            while True:
                await asyncio.sleep(1)  # Keep connection alive
    
    def start_websocket(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.websocket_handler())

def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    try:
        rclpy.spin(node)  # Keep the node alive
    finally:
        node.camera_thread.join()  # Wait for the camera thread to finish
        # node.websocket_thread.join()  # Wait for the WebSocket thread to finish
        rclpy.shutdown()

if __name__ == '__main__':
    main()
