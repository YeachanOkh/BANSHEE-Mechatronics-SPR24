import rclpy
from rclpy.node import Node
import cv2
import numpy as np
import threading
import asyncio
import ssl
import websockets
from std_msgs.msg import String

class CameraNode(Node):
    def __init__(self):
        super().__init__("camera_node")
        self.x_values_equal = 0
        self.arucoID = None
        self.websocket = None  # Initialize websocket attribute

        # ROS 2 subscription
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

        self.get_logger().info("Camera node initialized and camera & WebSocket threads started")

    def subscriberNode(self, msg):
        """ROS 2 subscriber callback to update arucoID from messages."""
        self.arucoID = int(msg.data)
        self.get_logger().info(f"Received Aruco ID: {self.arucoID}")

    def cameraRun(self):
        """Run the camera loop in a separate thread."""
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
        detector_parameters = cv2.aruco.DetectorParameters()
        refine_parameters = cv2.aruco.RefineParameters()
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.get_logger().error("Cannot open camera")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                self.get_logger().error("Can't receive frame. Exiting ...")
                break

            # Get frame dimensions and setup for marker detection
            height, width, _ = frame.shape
            box_size = 50
            box_x = int((width - box_size) / 2)
            box_y = int((height - box_size) / 2)

            # Detect ArUco markers
            detector = cv2.aruco.ArucoDetector(aruco_dict, detector_parameters, refine_parameters)
            marker_corners, marker_ids, _ = detector.detectMarkers(frame)

            # Only process if an Aruco ID is set via the subscriber
            if marker_ids is not None and self.arucoID is not None:
                for ids, corners in zip(marker_ids, marker_corners):
                    if ids == self.arucoID:
                        corner1_x = int(corners[0][0][0])
                        corner2_x = int(corners[0][2][0])
                        middle_x = (corner1_x + corner2_x) // 2
                        distance = abs(middle_x - int(width / 2))

                        cv2.putText(frame, f"distance: {distance}", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                        # Compute overlap ratio
                        middle_box = np.array([[box_x, box_y], [box_x + box_size, box_y + box_size]])
                        aruco_box = np.int32(corners[0])
                        intersection_area = cv2.contourArea(cv2.convexHull(np.concatenate([middle_box, aruco_box])))
                        union_area = box_size ** 2 + cv2.contourArea(cv2.convexHull(aruco_box)) - intersection_area
                        if union_area == 0:
                            union_area = 0.01
                        overlap_ratio = intersection_area / union_area

                        if overlap_ratio >= 0.98:
                            # Logic for arm activation (if needed)
                            pass

                        cv2.putText(frame, f"Overlap Ratio: {overlap_ratio:.2%}",
                                    (int(corners[0][:, 0].mean()), int(corners[0][:, 1].mean()) + 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Draw markers and the center box
            if marker_ids is not None:
                cv2.aruco.drawDetectedMarkers(frame, marker_corners, marker_ids)
            cv2.rectangle(frame, (box_x, box_y), (box_x + box_size, box_y + box_size), (0, 255, 0), 2)

            # Send frame over WebSocket (if connection is active)
            if self.websocket is not None:
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                asyncio.run(self.websocket.send(frame_bytes))  # Send frame bytes to WebSocket

            # Display the frame
            cv2.imshow("Camera live stream", frame)

            if cv2.waitKey(1) == ord('q'):
                exit()
                break

        cap.release()
        cv2.destroyAllWindows()

    async def websocket_handler(self):
        """WebSocket connection handler."""
        uri = "wss://rgs.bansheeuav.tech/ws"  # Replace with your WebSocket endpoint
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)

        async with websockets.connect(uri, ping_interval=30, ping_timeout=20, ssl=ssl_context) as websocket:
            self.websocket = websocket  # Set websocket attribute once connection is established
            self.get_logger().info("Connected to WebSocket server for sending frames")
            while True:
                await asyncio.sleep(1)  # Keep connection alive

    def start_websocket(self):
        """Start the asyncio event loop for WebSocket communication."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.websocket_handler())

def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    try:
        rclpy.spin(node)  # Keep the node alive
    except KeyboardInterrupt:
        pass
    finally:
        node.camera_thread.join()  # Wait for the camera thread to finish
        node.websocket_thread.join()  # Wait for the WebSocket thread to finish
        rclpy.shutdown()

if __name__ == '__main__':
    main()
