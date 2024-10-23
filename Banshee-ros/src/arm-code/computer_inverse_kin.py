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


PORT_NUM = 'COM10'  # for windows laptop
MOVEARM_MODE = 1
ADDR_PRESENT_POSITION = 132
ALL_IDs = [BASE_ID, BICEP_ID, FOREARM_ID, WRIST_ID, CLAW_ID]
MOVE_IDs = [BASE_ID, BICEP_ID, FOREARM_ID, WRIST_ID, CLAW_ID]

motor.portInitialization(PORT_NUM, ALL_IDs)
# ctrl.portInitialization(PORT_NUM, ALL_IDs)


#angle for the max length reaching out in the x pos
max_length_angle = calculation.angle_Calc([375, 0, 50], 0)

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

def debug_gcs_pullout():
    start_time = time.time()
    motor.dxlSetVelo([25, 25, 25, 25, 25], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)
    print("set up move")
    motor.simMotorRun([110, 223, 270, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up
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
    motor.simMotorRun([45], [3])  # Reset claw looking up
    time.sleep(0.8)

    print("move 8 pull forearm back")
    motor.simMotorRun([200], [2])  # Reset claw looking up
    time.sleep(0.25)

    print("move 9 pull forearm back")
    motor.simMotorRun([220], [4])  # Reset claw looking up
    time.sleep(0.4)

    motor.dxlSetVelo([15, 15, 15, 15, 15], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)

    print("move 13 pull forearm back")
    motor.simMotorRun([265, 47, 170], [2, 3, 4])
    time.sleep(0.8)
    #remove after open house
    print("move 14 pull forearm back")
    motor.simMotorRun([270], [4])
    time.sleep(0.8);
    print("set up move")
    motor.simMotorRun([30, 223, 270, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up

    time.sleep(1);
    print("set up move")
    motor.simMotorRun([110, 223, 270, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up
    end_time = time.time()
    print(end_time-start_time)


def debug_gcs_push_in():
    #Push In Battery
    start_time = time.time()
    motor.dxlSetVelo([15, 15, 15, 15, 15], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)

    print("move back to chamber")
    motor.simMotorRun([180, 62], [2, 3])
    time.sleep(2.5)

    motor.dxlSetVelo([50, 50, 50, 50, 50], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)

    gcs_push_in_angle = calculation.angle_Calc([310,0,65], 0)
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


bvm_max_length_angle = calculation.angle_Calc([375, 0, 70], 0)


def debug_bvm_pull_out():
    start_time = time.time()
    motor.dxlSetVelo([25, 25, 25, 25, 25], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)
    print("set up move")
    motor.simMotorRun([110, 223, 270, 47, 272], [0, 1, 2, 3, 4])  # Reset claw looking up
    time.sleep(2)

    print("move 1 move to chamber")
    motor.simMotorRun(bvm_max_length_angle, [1, 2, 3, 4])
    time.sleep(0.4)

    print("move 2 pitch wrist")
    motor.simMotorRun([200], [4])  # Reset claw looking up
    time.sleep(0.5)

    print("move 3 close grip")
    motor.simMotorRun([30], [0])  # Reset claw looking up
    time.sleep(0.1)

    # print("move 4 pull away slight")
    # motor.simMotorRun([225, 180, 199, 199], [1, 2, 3, 4])
    # time.sleep(0.15)
    # motor.dxlPresPos([0, 1, 2, 3, 4])
    for i in range(370,188,-2):
        print(i)
        initial_pull_out_angle = calculation.angle_Calc([i,0,67], 0)
        print("move 4 pull away slight")
        motor.simMotorRun(initial_pull_out_angle, [1, 2, 3, 4])
        time.sleep(0.05)
        motor.dxlPresPos([0, 1, 2, 3, 4])

    print("move 5 pull away more")
    motor.simMotorRun([225, 162, 72, 269], [1, 2, 3, 4])
    time.sleep(0.3)
    motor.dxlPresPos([0, 1, 2, 3, 4])

    print("move 6 pull away more")
    motor.simMotorRun([225, 180, 72, 269], [1, 2, 3, 4])
    time.sleep(0.3)
    motor.dxlPresPos([0, 1, 2, 3, 4])

    print("move 6 pull away more")
    motor.simMotorRun([225, 180, 60, 269], [1, 2, 3, 4])
    time.sleep(0.3)
    motor.dxlPresPos([0, 1, 2, 3, 4])
    
    for i in range(180,210,5):
        print(i)
        print("move 7 pull away more")
        motor.simMotorRun([225, i, 60, 269], [1, 2, 3, 4])
        time.sleep(0.05)
        motor.dxlPresPos([0, 1, 2, 3, 4])
    
    print("move 8 pull away more")
    motor.simMotorRun([225, 265, 60, 269], [1, 2, 3, 4])
    time.sleep(0.3)
    motor.dxlPresPos([0, 1, 2, 3, 4])

    print("move 9 pull away more")
    motor.simMotorRun([225, 265, 45, 269], [1, 2, 3, 4])
    time.sleep(0.3)
    motor.dxlPresPos([0, 1, 2, 3, 4])

    # final_pull_out_angle = calculation.angle_Calc([200,0,80], 0)
    # print("move 6 pull away even more")
    # ctrl.motorRun(final_pull_out_angle, [1, 2, 3, 4])
    # time.sleep(0.6)
    # ctrl.dxlPresPos([0, 1, 2, 3, 4])

def debug_bvm_push_in():
    #Push In Battery
    start_time = time.time()
    motor.dxlSetVelo([15, 15, 15, 15, 15], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    time.sleep(0.1)

    print("move back to chamber")
    motor.simMotorRun([220, 62], [2, 3])
    time.sleep(2)

    motor.simMotorRun([200, 62], [2, 3])
    time.sleep(1)

    motor.simMotorRun([190, 62], [2, 3])
    time.sleep(1)

    print("move back to chamber")
    motor.simMotorRun([180, 62], [2, 3])
    time.sleep(0.5)
    # motor.dxlPresPos([0, 1, 2, 3, 4])

    gcs_push_in_angle = calculation.angle_Calc([200,0,65], 0)
    print(gcs_push_in_angle)
    print("push in to chamber")
    motor.simMotorRun(gcs_push_in_angle, [1, 2, 3, 4])
    time.sleep(0.15)
    #[225, 160, 78, 266]
    # gcs_push_in_angle = calculation.angle_Calc([250,0,65], 0)
    # print(gcs_push_in_angle)
    print("push in to chamber")
    motor.simMotorRun([225, 130, 150, 230], [1, 2, 3, 4])
    time.sleep(0.15)

    print("push in to chamber")
    motor.simMotorRun([225, 120, 130, 210], [1, 2, 3, 4])
    time.sleep(0.15)

    print("push in to chamber")
    motor.simMotorRun([225, 110, 120, 200], [1, 2, 3, 4])
    time.sleep(0.15)

    print("push in to chamber")
    motor.simMotorRun([225, 110, 120, 200], [1, 2, 3, 4])
    time.sleep(0.15)

    # print("push in to chamber")
    # motor.simMotorRun([225, 90, 90, 180], [1, 2, 3, 4])
    # time.sleep(0.15)

    # gcs_push_in_angle = calculation.angle_Calc([300,0,65], 0)
    # print(gcs_push_in_angle)
    # print("push in to chamber")
    # motor.simMotorRun(gcs_push_in_angle, [1, 2, 3, 4])
    # time.sleep(0.15)
    # motor.dxlSetVelo([50, 50, 50, 50, 50], [0, 1, 2, 3, 4])  # ALWAYS SET SPEED BEFORE ANYTHING
    # time.sleep(0.1)

    # gcs_push_in_angle = calculation.angle_Calc([310,0,65], 0)
    # print(gcs_push_in_angle)
    # print("push in to chamber")
    # motor.simMotorRun(gcs_push_in_angle, [1, 2, 3, 4])
    # time.sleep(0.15)

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
    # debug_gcs_pullout()
    # # time.sleep(5)
    # # debug_gcs_push_in()
    
    debug_bvm_pull_out()
    time.sleep(3)
    # debug_bvm_push_in()
    