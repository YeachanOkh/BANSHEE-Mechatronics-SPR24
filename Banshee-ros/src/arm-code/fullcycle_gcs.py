import math
import motorctrl_v1 as motor
import Movement_Calc_v2 as calculation
import numpy as np
import time
import serial
import cv2
import socket

BASE_ID = 1
BICEP_ID = 2
FOREARM_ID = 3
WRIST_ID = 4
CLAW_ID = 0


# PORT_NUM = '/dev/cu.usbserial-FT5NY9DI'  #for mac
PORT_NUM = '/dev/ttyUSB0'  # for rpi
ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)  # for rpi

BAUDRATE = 1000000
MOVEARM_MODE = 1
ADDR_PRESENT_POSITION = 132
ALL_IDs = [BASE_ID, BICEP_ID, FOREARM_ID, WRIST_ID, CLAW_ID]
MOVE_IDs = [BASE_ID, BICEP_ID, FOREARM_ID, WRIST_ID, CLAW_ID]

motor.portInitialization(PORT_NUM, ALL_IDs)
SERVER_HOST = '192.168.1.41'
SERVER_PORT = 3300

bvm_max_length_angle = calculation.angle_Calc([370, 0, 75], 0)

def checkMovement(ids):
    motorStatus = [0] * len(ids)
    finished = [1] * len(ids)
    firstPosition = 0
    secondPosition = 0
    while True:
        for id in (ids):
            firstPosition = motor.ReadMotorData(id, ADDR_PRESENT_POSITION)
            time.sleep(.1)
            secondPosition = motor.ReadMotorData(id, ADDR_PRESENT_POSITION)
            if (abs(firstPosition - secondPosition) < 5):
                motorStatus[id] = 1
        if (motorStatus == finished):
            print("finished")
            break
        
    
max_length_angle = calculation.angle_Calc([375, 0, 50], 0)
def debug_gcs_push_in():
    #Push In Battery
    start_time = time.time()
    motor.dxlSetVelo([15, 15, 15, 15, 15], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)
    #265, 47, 170
    print("move back to chamber1")
    motor.simMotorRun([270, 54], [2, 3])
    time.sleep(2.5)

    print("move back to chamber2")
    motor.simMotorRun([180, 56], [2, 3])
    time.sleep(3)

    print("move back to chamber2")
    motor.simMotorRun([180, 62], [2, 3])
    time.sleep(2.5)
    motor.dxlSetVelo([40, 40, 40, 40, 40], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)

    gcs_push_in_angle = calculation.angle_Calc([310,0,70], 0)
    print(gcs_push_in_angle)
    print("push in to chamber")
    motor.simMotorRun(gcs_push_in_angle, [1, 2, 3, 4])
    time.sleep(0.15)

    print("push all the way in to chamber")
    motor.simMotorRun(max_length_angle, [1, 2, 3, 4])
    time.sleep(0.15)

    print("open claw")
    motor.simMotorRun([110], [0])  # Reset claw looking up
    time.sleep(0.15)

    gcs_pull_out_angle = calculation.angle_Calc([300,0,60], 0)
    print("move 4 pull away slight")
    motor.simMotorRun(gcs_pull_out_angle, [1, 2, 3, 4])
    time.sleep(1.5)

    print("set up move")
    motor.simMotorRun([110, 223, 270, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up
    end_time = time.time()
    print(end_time-start_time)


def debug_gcs_pull_out():
    start_time = time.time()
    motor.dxlSetVelo([25, 25, 25, 25, 25], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)
    print("set up move")
    motor.simMotorRun([93, 223, 270, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up
    time.sleep(2)

    print("move 1 move to chamber")
    motor.simMotorRun(max_length_angle, [1, 2, 3, 4])
    time.sleep(0.4)

    print("move 2 pitch wrist")
    motor.simMotorRun([200], [4])  # Reset claw looking up
    time.sleep(0.5)

    print("move 3 close grip")
    motor.simMotorRun([30], [0])  # Reset claw looking up
    time.sleep(0.1)

    print("move 4 pull forearm back")
    motor.simMotorRun([160], [3])  # Reset claw looking up
    time.sleep(0.15)

    inital_pull_out_angle = calculation.angle_Calc([300,0,60], 0)
    print("move 4 pull away slight")
    motor.simMotorRun(inital_pull_out_angle, [1, 2, 3, 4])
    time.sleep(0.15)

    second_pull_out_angle = calculation.angle_Calc([250,0,60], 0)
    print("move 5 pull away more")
    motor.simMotorRun(second_pull_out_angle, [1, 2, 3, 4])
    time.sleep(0.3)

    final_pull_out_angle = calculation.angle_Calc([200,0,60], 0)
    print("move 6 pull away even more")
    motor.simMotorRun(final_pull_out_angle, [1, 2, 3, 4])
    time.sleep(0.6)

    print("move 7 pull forearm back")
    motor.simMotorRun([49], [3])  # Reset claw looking up
    time.sleep(0.8)

    print("move 8 pull forearm back")
    motor.simMotorRun([200], [2])  # Reset claw looking up
    time.sleep(0.25)

    print("move 9 pull forearm back")
    motor.simMotorRun([220], [4])  # Reset claw looking up
    time.sleep(0.4)

    motor.dxlSetVelo([15, 15, 30, 15, 15], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)

    print("move 13 pull forearm back")
    motor.simMotorRun([265, 47, 170], [2, 3, 4])
    time.sleep(0.8)

    print("move 14 pull forearm back")
    motor.simMotorRun([270], [4])
    end_time = time.time()
    print(end_time-start_time)

bvm_max_length_angle = calculation.angle_Calc([367, -3, 73], 0)

def debug_bvm_pull_out():
    start_time = time.time()
    motor.dxlSetVelo([30, 30, 30, 30, 30], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)

    print("set up move")
    motor.simMotorRun([98, 225, 260, 50, 278], [0, 1, 2, 3, 4])  # Reset claw looking up
    time.sleep(2)

    print("move 1 move to chamber")
    motor.simMotorRun(bvm_max_length_angle, [1,2, 3, 4])
    time.sleep(1)
    print("move 2 pitch wrist")
    motor.simMotorRun([123,200], [2,4])  # Reset claw looking up
    time.sleep(1)

    print("move 3 close grip")
    motor.simMotorRun([30], [0])  # Reset claw looking up
    time.sleep(0.5)

    for i in range(280,190,-10):
        print(i)
        initial_pull_out_angle = calculation.angle_Calc([i,-3,73], 0)
        print("move 4 pull away slight")
        motor.simMotorRun(initial_pull_out_angle, [1, 2, 3, 4])
        time.sleep(.2)
        motor.dxlPresPos([0, 1, 2, 3, 4])

    print("set up move")
    motor.simMotorRun([30, 222, 260, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up
    time.sleep(2)

def debug_bvm_push_in():
    #Push In Battery
    start_time = time.time()
    motor.dxlSetVelo([30, 30, 30, 30, 30], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)

    gcs_push_in_angle = calculation.angle_Calc([180,-2,73], 0)
    print(gcs_push_in_angle)
    print("move back in to chamber")
    motor.simMotorRun(gcs_push_in_angle, [1, 2, 3, 4])
    time.sleep(1)

    #[223, 115, 191, 197] 1 2 3 4 
    print("adjust")
    for i in range(190,380,10):
        print(i)
        initial_push_angle = calculation.angle_Calc([i,-3,73], 0)
        print("push 4 slight")
        motor.simMotorRun(initial_push_angle, [1, 2, 3, 4])
        time.sleep(.1)
        motor.dxlPresPos([0, 1, 2, 3, 4])

    motor.simMotorRun([30, 223, 113, 210, 186], [0, 1, 2, 3, 4])
    time.sleep(0.5)

    motor.simMotorRun([100],[0])
    time.sleep(0.025)

    motor.simMotorRun([200],[1])
    motor.simMotorRun([240],[1])
    time.sleep(1)
    motor.simMotorRun([225],[1])
    motor.simMotorRun([270,47,250],[2,3,4])
    time.sleep(0.5)
    print("set up move")
    motor.simMotorRun([98, 225, 260, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up
    time.sleep(2)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))


arduinoinput = ''
# TCP IP request from GCS.
client_socket.send("Mech".encode('utf-8'))
while True:
    response = client_socket.recv(1024)
    if response.decode() == 'G':
        break

# Take Battery from GCS
debug_gcs_pullout()
GPIO.output(22, GPIO.HIGH)
time.sleep(8)
ser.write(b'b')  # Tell Arduino it's good to go

# Wait for arduino to send s, means it has arrived at BVM
while True:
    print("waiting for s")
    response = ser.readline().strip()
    arduinoinput = response.decode()
    if arduinoinput == 's':
        print("push battery into BVM!")
        break


# Push battery into BVM
ser.flush()
time.sleep(3)
debug_bvm_push_in()

time.sleep(8)  # let BVM cycle battery

# Take battery out of BVM
debug_bvm_pull_out()
time.sleep(3)
print("sending g to arduino")
ser.write(b'g')  # Tell Arduino it's good to go
time.sleep(0.5)
response = ser.readline().strip().decode()
print(response)

# Wait for arduino to send s, means it has arrived at GCS
while True:
    response = ser.readline().strip()
    arduinoinput = response.decode()
    if arduinoinput == 's':
        print("push battery into GCS!")
        break

# Push battery into GCS

debug_gcs_push_in()

# Tell GCS it's good to go
message = 'Finished'
client_socket.send(message.encode())
GPIO.cleanup()