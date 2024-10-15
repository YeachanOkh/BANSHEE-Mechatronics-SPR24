import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SendArucoID(Node):
    def __init__(self):
        super().__init__("Arucopublisher_node")
        self.publisher = self.create_publisher(
            String,
            'arucoID',
            10
        )
        self.get_logger().info("ArucoID Publisher started")
        self.publisher_node()
    
    def publisher_node(self):
        msg = String()
        msg.data = input("Input Aruco Marker: ")
        self.publisher.publish(msg)
        self.get_logger().info('Sent marker: "%s"' % msg.data)
        self.publisher_node()
    
def main(args=None):
    rclpy.init(args=args)
    node = SendArucoID()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

