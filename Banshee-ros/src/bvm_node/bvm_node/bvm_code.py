import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int8
import serial
import time
import struct
import glob
#drone battery 4-5
#battery columns 0-3
#we get drone landed done from gcs node (mode 1)
#voltage from esp and find lowest aruco with no voltage
#find max voltage battery lowest aruco
#back to drone aruco we previously
def find_esp_port():
    """Finds the correct Pixhawk serial port (if00)."""
    serial_ports = glob.glob('/dev/serial/by-id/*')

    for port in serial_ports:
        if "Silicon_Labs" in port:
            print(f"Found esp port: {port}")
            return port

class BVMNode(Node):
    def __init__(self):
        super().__init__("BVM_Node")

        # Mode 0 = standby
        # Mode 1 = Pull Drone/BVM
        # Mode 2 = Push BVM/Drone
        # Mode 3 = Check if cycle done or continue cycle (mode 0 or mode 1)
        self.mode = 0 # decides what bvmlogic function will do
        self.done = 0 # flag for each mode
        self.halfCycleComplete = 0 # flag to choose whether drone battery or bvm battery chamber
        self.DroneMarkers = [8]
        self.batteryChamber = None # Full battery chamber
        self.emptyChamber = None # Empty battery chamber
        self.ser = serial.Serial(find_esp_port(), 115200, timeout=None)


        self.arucoPublisher = self.create_publisher(
        Int8, 'arucoID', 10)
        self.get_logger().info("ArucoID Publisher started")

        self.resetStepperPublisher = self.create_publisher(
        Int8, 'reset', 10)

        self.armSubscriber = self.create_subscription(
        Bool, 'ArmDone', self.modeComplete, 10)

        # Only use function below for testing purposes
        # self.arucoIDPublisher()

        self.run_timer = self.create_timer(0.1, self.bvmLogic)
    
    # Function for testing purposes
    def arucoIDPublisher(self, aruco_ID):
        msg = Int8()
        msg.data = aruco_ID
        self.arucoPublisher.publish(msg)
        self.get_logger().info(f"Sent marker: {msg.data}")
    
    def publish_reset_stepper(self):
        msg = Int8()          
        msg.data = 0          
        self.resetStepperPublisher.publish(msg)
        self.get_logger().info("Reset signal sent to stepper motor.")

    # Triggers when arm sends complete signal
    def modeComplete(self, msg):
        if msg.data:
            self.done = 0
            self.mode += 1
    
    # Potential subscriber if we want camera to check # of batteries on drone (not in use)
    def getDroneMarkers(self, msg):
        self.DroneMarkers = []

    # Used to decode byte messages from ESP UART serial port
    def structUnpack(self, type, data):
        try:
            return [round(v,2) for v in struct.unpack(type, data)]
        except:
            self.get_logger().info("Incomplete data received")

    # Reads from ESP UART serial port once each iteration
    def espRead(self):
        if self.ser.in_waiting > 0:
            tag = self.ser.readline().decode('utf-8').strip()
            # Examples of reading from ESP
            if tag == "Voltage":
                raw_data = self.ser.read(32)
                values = self.structUnpack('8f', raw_data)
                self.batteryChamber = values.index(max(values))
                self.emptyChamber = values.index(min(values))
                self.mode = 1
            else:
                return
            self.get_logger().info("Tag: " + tag)
            self.get_logger().info(f"{values}")

    # Sends 2 new lines into ESP UART serial port
    # def espSend(self, tag, data=None):
    #     try:
    #         self.ser = serial.Serial(find_esp_port(), 115200, timeout=None)
    #     except:
    #         self.ser.close()
    #         time.sleep(1)
    #         self.ser = serial.Serial(find_esp_port(), 115200, timeout=None)
    #     tag = str(tag)
    #     self.ser.write((tag + '\n').encode('utf-8'))
    #     if data != None:
    #         data = str(data)
    #         self.ser.write((data + '\n').encode('utf-8'))
    #     self.ser.close()
    #     time.sleep(1)
    #     self.ser = serial.Serial(find_esp_port(), 115200, timeout=None)

    def espSend(self, tag, data=None):
        if not self.ser.is_open:
            self.ser.open()

        try:
            tag = str(tag)
            self.ser.write((tag + '\n').encode('utf-8'))
            time.sleep(0.1)  # Give the ESP time to process

            if data is not None:
                data = str(data)
                self.ser.write((data + '\n').encode('utf-8'))
                time.sleep(0.1)

            self.ser.flush()
            self.get_logger().info(f"Sent to ESP: {tag}, {data}")

        except serial.SerialException as e:
            self.get_logger().error(f"Serial write failed: {e}")
    
    # Logic of the program
    def bvmLogic(self):
        if self.ser.is_open:
            pass
        else:
            self.ser = serial.Serial(find_esp_port(), 115200, timeout=None)

        if self.mode == 0:
            self.espRead()
        
        # Mode 1: Pull Drone, (2)pull full
        elif self.mode == 1 and self.done == 0:
            if self.halfCycleComplete == 0:
                aruco_ID = self.DroneMarkers[0]
            else:
                aruco_ID = self.batteryChamber
                if self.ser.is_open:
                    self.espSend("Unlock", aruco_ID)
                    self.get_logger().info("Push Unlock signal reached")
                else:
                    self.get_logger().info("Unlock signal not reached")
            msg = Int8()
            msg.data = aruco_ID
            self.arucoPublisher.publish(msg)
            self.get_logger().info('Sent marker: "%s"' % msg.data)
            self.done = 1

        # Mode 2: push empty, (2)push drone
        elif self.mode == 2 and self.done == 0:
            if self.halfCycleComplete == 0:
                aruco_ID = self.emptyChamber
                if self.ser.is_open:
                    self.espSend("Unlock", aruco_ID)
                    self.get_logger().info("Push Unlock signal reached")
                else:
                    self.get_logger().info("Unlock signal not reached")
            else:
                aruco_ID = self.DroneMarkers[0]
            msg = Int8()
            msg.data = aruco_ID
            self.arucoPublisher.publish(msg)
            self.get_logger().info('Sent marker: "%s"' % msg.data)
            self.done = 1

        elif self.mode == 3:
            if self.halfCycleComplete == 0:
                self.mode = 1
                self.halfCycleComplete = 1
            else:
                self.DroneMarkers.pop(0)
                if len(self.DroneMarkers) > 1:
                    self.espSend("CycleComplete")
                else:
                    self.espSend("DroneComplete")
                    self.DroneMarkers = [8] # Only 1 index since we do not have function to find batteries yet, and only 1 battery on drone for now.
                    self.publish_reset_stepper()
                self.mode = 0
                self.halfCycleComplete = 0
            # determine whether to go to mode 1 or 0, based on drone array 
            # if drone array has number go to mode 1 and pull that number if drone array empty go to mode 0
            #drone array get rid of one index

    
def main(args=None):
    rclpy.init(args=args)
    node = BVMNode()
    try:
        rclpy.spin(node)
    except:
        KeyboardInterrupt
if __name__ == '__main__':
    main()