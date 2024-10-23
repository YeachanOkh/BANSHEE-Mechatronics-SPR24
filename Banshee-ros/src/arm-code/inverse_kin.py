import math
import motorctrl_v1 as motor
import motorctrl_v2 as ctrl
import Movement_Calc_v2 as calculation
import numpy as np
import time
import cv2
import socket

#Distance from BVM to BTP 16.5 inches

BASE_ID = 1
BICEP_ID = 2
FOREARM_ID = 3
WRIST_ID = 4
CLAW_ID = 0


PORT_NUM = '/dev/ttyUSB0'  # for rpi
MOVEARM_MODE = 1
ADDR_PRESENT_POSITION = 132
ALL_IDs = [BASE_ID, BICEP_ID, FOREARM_ID, WRIST_ID, CLAW_ID]
MOVE_IDs = [BASE_ID, BICEP_ID, FOREARM_ID, WRIST_ID, CLAW_ID]

motor.portInitialization(PORT_NUM, ALL_IDs)
ctrl.portInitialization(PORT_NUM, ALL_IDs)


#angle for the max length reaching out in the x pos
max_length_angle = calculation.angle_Calc([375, 0, 73], 0)

#"[%s, %s, %s, %s]" % (int(baseTheta), int(shoulderTheta), int(elbowTheta), int(wristTheta))

def checkMovement(ids):
    motorStatus = [0] * len(ids)
    finished = [1] * len(ids)
    firstPosition = 0
    secondPosition = 0
    while True:
        for id in (ids):
            firstPosition = ctrl.ReadMotorData(id, ADDR_PRESENT_POSITION)
            time.sleep(.1)
            secondPosition = ctrl.ReadMotorData(id, ADDR_PRESENT_POSITION)
            if (abs(firstPosition - secondPosition) < 5):
                motorStatus[id] = 1
        if (motorStatus == finished):
            print("finished")
            break

def time_between_moves(velocity: list[int], ids: list[int], startAngles: list[int], midAngles: list[int], endAngles: list[int]) -> None:
    ctrl.dxlSetVelo(velocity, ids)  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)
    print("Move 1")
    ctrl.motorRun(startAngles, ids)  # Reset claw looking up
    start_time = time.time()
    checkMovement(ids)

    check_time = time.time()

    print("Move 2")
    check_time2 = time.time()
    ctrl.motorRun(midAngles, ids)
    checkMovement(ids)

    print("Move 3")
    ctrl.motorRun(endAngles, ids)
    end_time = time.time()

    # print("total time")
    # print(end_time-start_time)
    # print("check time")
    # print(check_time-start_time)
    # print("check2 time")
    # print(check_time2-start_time)
    # print("check to check time")
    # print(check_time2-check_time)

def move(velocity: list[int], ids: list[int], startAngles: list[int], midAngles: list[int], endAngles: list[int]) -> None:
    # ctrl.dxlSetVelo(velocity, ids)  # ALWAYS SET SPEED BEFORE ANYTHING
    # time.sleep(0.1)
    # print("Sleep move")
    # print("Move 1")
    # ctrl.motorRun(startAngles, ids)  # Reset claw looking up
    # time.sleep(3)
    # print("Move 2")
    # ctrl.motorRun(midAngles, ids)
    # time.sleep(3)
    # print("Move 3")
    # ctrl.motorRun(endAngles, ids)

    print("Optimized Move")
    print("Move 1.2")
    ctrl.motorRun(startAngles, ids)  # Reset claw looking up
    time.sleep(1)
    start_time = time.time()
    print("Move 2.2")
    ctrl.motorRun(midAngles, ids)
    time.sleep(0.1)
    print("Move 3.2")
    ctrl.motorRun(endAngles, ids)
    end_time = time.time()
    print(end_time)

def sleepless_move(velocity: list[int], ids: list[int], startAngles: list[int], midAngles: list[int], endAngles: list[int]) -> None:
    ctrl.dxlSetVelo(velocity, ids)  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)
    print("Sleepless move")
    print("Move 1")
    ctrl.motorRun(startAngles, ids)  # Reset claw looking up
    print("Move 2")
    ctrl.motorRun(midAngles, ids)
    print("Move 3")
    ctrl.motorRun(endAngles, ids)


def debug_gcs_push_in():
    #Push In Battery
    start_time = time.time()
    motor.dxlSetVelo([30, 30, 30, 30, 30], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)
    #265, 47, 170

    print("move back to chamber2")
    motor.simMotorRun([180, 56], [2, 3])
    time.sleep(3)

    print("move back to chamber2")
    motor.simMotorRun([180, 70], [2, 3])
    time.sleep(2.5)
    motor.dxlSetVelo([40, 40, 40, 40, 40], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)

    print("adjust")
    for i in range(190,380,10):
        print(i)
        initial_push_angle = calculation.angle_Calc([i,-3,72], 0)
        print("push 4 slight")
        motor.simMotorRun(initial_push_angle, [1, 2, 3, 4])
        time.sleep(.1)
        motor.dxlPresPos([0, 1, 2, 3, 4])

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
    motor.simMotorRun([98, 225, 260, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up
    time.sleep(1)


def debug_gcs_pull_out():
    start_time = time.time()
    motor.dxlSetVelo([30, 30, 30, 30, 30], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)
    print("set up move")
    motor.simMotorRun([93, 223, 270, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up
    time.sleep(2)

    print("move 1 move to chamber")
    motor.simMotorRun(max_length_angle, [1, 2, 3, 4])
    time.sleep(0.4)
    motor.simMotorRun([30, 223, 113, 210, 186], [0, 1, 2, 3, 4])
    time.sleep(0.5)
    print("move 2 pitch wrist")
    motor.simMotorRun([200], [4])  # Reset claw looking up
    time.sleep(0.5)

    print("move 3 close grip")
    motor.simMotorRun([30], [0])  # Reset claw looking up
    time.sleep(0.1)

    print("move 4 pull forearm back")
    motor.simMotorRun([160], [3])  # Reset claw looking up
    time.sleep(0.15)

    # inital_pull_out_angle = calculation.angle_Calc([300,0,60], 0)
    # print("move 4 pull away slight")
    # motor.simMotorRun(inital_pull_out_angle, [1, 2, 3, 4])
    # time.sleep(0.15)

    # second_pull_out_angle = calculation.angle_Calc([250,0,60], 0)
    # print("move 5 pull away more")
    # motor.simMotorRun(second_pull_out_angle, [1, 2, 3, 4])
    # time.sleep(0.3)

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

    print("set up move")
    motor.simMotorRun([30, 225, 260, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up
    time.sleep(1)

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
    motor.simMotorRun([124,200], [2,4])  # Reset claw looking up
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

    print("set up move")
    motor.simMotorRun([30, 222, 260, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up
    time.sleep(2)


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
    

if __name__ == "__main__":
    # velocity = [25, 25, 25, 25, 25]
    # ids = [0, 1, 2, 3, 4]
    # startAngles = [110, 223, 270, 47, 160]
    # midAngles = [110, 223, 250, 60, 220]
    # endAngles = [110, 223, 210, 80, 270]
    # time_between_moves(velocity=velocity, ids=ids, startAngles=startAngles, midAngles=midAngles, endAngles=endAngles)
    # time.sleep(5)
    # move(velocity=velocity, ids=ids, startAngles=startAngles, midAngles=midAngles, endAngles=endAngles)
    # gcs_pullout()
    debug_gcs_pull_out()
    time.sleep(5)
    debug_gcs_push_in()
    
    # debug_bvm_pull_out()
    # time.sleep(5)
    # debug_bvm_push_in()