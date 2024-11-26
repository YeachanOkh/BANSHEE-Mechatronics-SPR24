#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int8, String  # Import message type for the 'done' signal
import math
from integration import motorctrl_v2 as motor
from integration import Movement_calc_v2 as calculation
import numpy as np
import time
import cv2

# Define motor ID
BASE_ID = 1
BICEP_ID = 2
FOREARM_ID = 3
WRIST_ID = 4
CLAW_ID = 0


# Define port number for Raspberry Pi
PORT_NUM = '/dev/ttyUSB0'  # for rpi


# Define move mode and address for present position
MOVEARM_MODE = 1
ADDR_PRESENT_POSITION = 132


# List of all motor IDs
ALL_IDs = [BASE_ID, BICEP_ID, FOREARM_ID, WRIST_ID, CLAW_ID]
MOVE_IDs = [BASE_ID, BICEP_ID, FOREARM_ID, WRIST_ID, CLAW_ID]


# Initialize motor port
motor.portInitialization(PORT_NUM, ALL_IDs)


# Calculate the angle for the max length reaching out in the x position
max_length_angle = calculation.angle_Calc([375, 0, 73], 0)

# define
TOP_BVM = 0
BOT_BVM = 1
DRONE_BAT = 2

# Upper BVM batteries when dev = 0
# Lower BVM batteries when dev = 1
# Drone batteries when dev = 2

# def pull_out(dev):
#     if dev == 0:
#         motor.dxlSetVelo([30, 30, 30, 30, 10], [0, 1, 2, 3, 4])
#         # motor.simMotorRun([x,x,x,x,x],[0,1,2,3,4])
#         time.sleep(1)
#     elif dev == 1:
#         motor.dxlSetVelo([30, 30, 30, 30, 10], [0, 1, 2, 3, 4])
#         # motor.simMotorRun([x,x,x,x,x],[0,1,2,3,4])
#         time.sleep(1)
#     elif dev == 2:
#         motor.dxlSetVelo([30, 30, 30, 30, 10], [0, 1, 2, 3, 4])
#         # motor.simMotorRun([x,x,x,x,x],[0,1,2,3,4])
#         time.sleep(1)
#     else:
#         print("INVALID")

# def push_in(dev):
#     if dev == 0:
#         motor.dxlSetVelo([30, 30, 30, 30, 10], [0, 1, 2, 3, 4])
#         # motor.simMotorRun([x,x,x,x,x],[0,1,2,3,4])
#         time.sleep(1)
#     elif dev == 1:
#         motor.dxlSetVelo([30, 30, 30, 30, 10], [0, 1, 2, 3, 4])
#         # motor.simMotorRun([x,x,x,x,x],[0,1,2,3,4])
#         time.sleep(1)
#     elif dev == 2:
#         motor.dxlSetVelo([30, 30, 30, 30, 10], [0, 1, 2, 3, 4])
#         # motor.simMotorRun([x,x,x,x,x],[0,1,2,3,4])
#         time.sleep(1)
#     else:
#         print("INVALID")


# Grab high
def Grab_high():
    start_time = time.time()
    print("Grabbing high")
    motor.dxlSetVelo([30, 30, 10, 10, 10], [0, 1, 2, 3, 4])
    motor.simMotorRun([170, 330, 90],[2, 3, 4])
    time.sleep(0.1)

# Grab low
def Grab_low():
    start_time = time.time()
    print("Grabbing low")
    motor.dxlSetVelo([30, 30, 10, 10, 10], [0, 1, 2, 3, 4])
    motor.simMotorRun([132, 347, 54],[2, 3, 4])
    time.sleep(0.1)

def Drone_grab():
    start_time = time.time()
    print("Grabbing drone")
    motor.dxlSetVelo([10, 10, 10], [2, 3, 4])
    motor.simMotorRun([132, 347, 54],[2, 3, 4])

#######

def Push_low():    
    start_time = time.time()
    print("Push in low sequence")
    motor.dxlSetVelo([10, 10, 10], [2, 3, 4])
    motor.simMotorRun([132, 343, 70],[2, 3, 4]) # guesstimate
    time.sleep(5)
    motor.dxlSetVelo([10, 8, 5], [2, 3, 4])
    motor.simMotorRun([110, 330, 60],[2, 3, 4])
    time.sleep(2)
    motor.dxlSetVelo([10, 8, 10], [2, 3, 4])
    motor.simMotorRun([100, 320, 50],[2, 3, 4])
    time.sleep(1)
    # slight push
    motor.simMotorRun([310, 65],[3, 4])
    time.sleep(1)
    motor.simMotorRun([290, 75],[3, 4])
    time.sleep(1)
    motor.simMotorRun([90, 270, 90],[2, 3, 4])
    time.sleep(1)
    motor.simMotorRun([80, 260, 95],[2, 3, 4])

########

def Push_high():    
    start_time = time.time()
    print("Push in low sequence")
    motor.dxlSetVelo([30, 30, 10, 10, 10], [0, 1, 2, 3, 4])
    motor.simMotorRun([120, 250, 80],[2, 3, 4]) # guesstimate
    time.sleep(0.1)


# Close Claw
def Close():
    start_time = time.time()
    print("close claw")
    motor.dxlSetVelo([30, 30, 30, 30, 10], [0, 1, 2, 3, 4])
    motor.simMotorRun([108],[0])
    time.sleep(1)
    # motor.simMotorRun([134],[1])

#Open Claw
def Open():
    start_time = time.time()
    print("open claw")
    motor.dxlSetVelo([30, 30, 30, 30, 10], [0, 1, 2, 3, 4])
    motor.simMotorRun([45],[0])
    time.sleep(1)

# Setup initial motor positions
def startsetup():
    print("setting up")
    motor.dxlSetVelo([30, 30, 30, 30, 10], [0, 1, 2, 3, 4])
    motor.simMotorRun([224, 222, 347, 139], [1, 2, 3, 4])
    time.sleep(1)

# Dictionary mapping commands to functions
Command_dict = {
    "grab high": Grab_high,
    "grab low": Grab_low,
    "push low": Push_low,
    "push high": Push_high,
    "drone grab": Drone_grab,
    "close": Close,
    "open": Open,
    "setup": startsetup,
}

# Mode-to-action mapping
MODE_0 = {
    0: Grab_high,
    1: Grab_low,
    2: Drone_grab
}

MODE_1 = {
    0: Push_high,
    1: Push_low,
    2: Drone_push
}

class IntegrationNode(Node):
    def __init__(self):
        super().__init__('Integration_Node')
        self.mode = 0
        self.get_logger().info("Integration Node has started.")
        
        # Subscriber for commands
        self.armCommand = self.create_subscription(
          Int8,'DestinationConfirm', self.done_callback, 10)
        
        # Publisher for task completion
        self.armFinished = self.create_publisher(
          Bool, 'ArmDone', 10)
        
    def done_callback(self, msg):
        command = msg.data
        self.get_logger().info(f"Received command: {command} in Mode {self.mode}")

        # Execute action based on mode and command
        if self.mode == 0:
            MODE_0[command]()
            self.mode = 1  # Switch to Mode 1 after execution
        elif self.mode == 1:
            MODE_1[command]()
            self.mode = 0  # Switch back to Mode 0 after execution
        else:
            self.get_logger().warning(f"Invalid command: {command} for Mode {self.mode}")

        self.arm_done()

    def arm_done(self):
        task_done_msg = Bool()
        task_done_msg.data = True
        self.armFinished.publish(task_done_msg)
        self.get_logger().info("Task completed signal published.")

def main(args=None):
    rclpy.init(args=args)
    node = IntegrationNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()