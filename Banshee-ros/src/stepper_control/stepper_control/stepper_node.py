import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool  # Add Bool for the 'done' signal
import RPi.GPIO as GPIO
from time import sleep

class StepperMotorNode(Node):
    def __init__(self):
        super().__init__('stepper_motor_node')

        # Pin setup
        self.DIR = 10  # Direction pin
        self.STEP = 8  # Step pin
        self.CW = 1    # Clockwise
        self.CCW = 0   # Counterclockwise

        # GPIO setup
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.DIR, GPIO.OUT)
        GPIO.setup(self.STEP, GPIO.OUT)

        # Set initial direction
        GPIO.output(self.DIR, self.CW)

        # Initialize step counts
        self.step_count_cw = 0
        self.step_count_ccw = 0
        self.is_cw = True  # Track the current direction

        # Publishers
        self.publisher_ = self.create_publisher(String, 'motor_status', 10)
        self.done_publisher = self.create_publisher(Bool, '/stepper/done', 10)  # Publish 'done' signal
        
        # Subscriber: listen for direction change commands
        self.subscriber_ = self.create_subscription(
            String,
            'motor_command',
            self.command_callback,
            10
        )

        self.timer = self.create_timer(0.01, self.control_stepper) 

    def command_callback(self, msg):
        """Callback function for subscriber to change direction."""
        command = msg.data.lower()
        if command == 'cw':
            self.get_logger().info("Received command to move CW")
            GPIO.output(self.DIR, self.CW)
            self.is_cw = True
        elif command == 'ccw':
            self.get_logger().info("Received command to move CCW")
            GPIO.output(self.DIR, self.CCW)
            self.is_cw = False

    def control_stepper(self):
        if self.is_cw:
            if self.step_count_cw < 20000:  # CW movement
                self.step_motor()
                self.step_count_cw += 1
            else:
                self.get_logger().info("Changing direction to CCW")
                GPIO.output(self.DIR, self.CCW)
                self.is_cw = False 
                self.step_count_cw = 0 
                sleep(1.0) 
                self.publish_done_signal()  # Publish 'done' signal when finished CW movement
        else:
            if self.step_count_ccw < 200: 
                self.step_motor()
                self.step_count_ccw += 1
            else:
                self.get_logger().info("Changing direction to CW")
                GPIO.output(self.DIR, self.CW)
                self.is_cw = True 
                self.step_count_ccw = 0 
                sleep(1.0)  
                self.publish_done_signal()  # Publish 'done' signal when finished CCW movement

        # Publish motor status
        status_msg = String()
        direction = "CW" if self.is_cw else "CCW"
        status_msg.data = f"Direction: {direction}, Steps CW: {self.step_count_cw}, Steps CCW: {self.step_count_ccw}"
        self.publisher_.publish(status_msg)

    def publish_done_signal(self):
        """Publish a done signal for the Integration Node."""
        done_msg = Bool()
        done_msg.data = True
        self.done_publisher.publish(done_msg)
        self.get_logger().info("Published 'done' signal.")

    def step_motor(self):
        GPIO.output(self.STEP, GPIO.HIGH)
        sleep(0.0001)  # Speed control
        GPIO.output(self.STEP, GPIO.LOW)
        sleep(0.0001)  # Speed control

    def destroy_node(self):
        GPIO.cleanup()  
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    stepper_node = StepperMotorNode()

    try:
        rclpy.spin(stepper_node)
    except KeyboardInterrupt:
        pass
    finally:
        stepper_node.destroy_node()
        GPIO.cleanup()
        rclpy.shutdown()

if __name__ == '__main__':
    main()