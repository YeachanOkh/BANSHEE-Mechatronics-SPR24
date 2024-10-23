import cv2
import matplotlib.pyplot as plt     
from cv2 import aruco
import numpy as np
import time
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
    # boolean to determine if arm is in right positiono with battery
    armstart=False
    # Get frame dimensions
    height, width, _ = frame.shape
    #set middle box height and weight
    box_size = 50
    box_x = int((width - box_size) / 2)
    box_y = int((height - box_size) / 2)

    # 4. Detect ArUco markers
    detector = cv2.aruco.ArucoDetector(aruco_dict, detector_parameters, refine_parameters)

    marker_corners, marker_ids, rejectedImgPoints = detector.detectMarkers(frame)

    id_needed = 1

    # 5. Draw detected markers on the frame and calculate overlap
    # check to see if ar marker is being recognized
    if marker_ids is not None:
        for ids, corners in zip(marker_ids, marker_corners):

           # Calculate the overlap between the middle box and ArUco marker detection box
            middle_box = np.array([[box_x, box_y], [box_x + box_size, box_y + box_size]])
            aruco_box = np.int32(corners[0])  # Convert corners to integer for calculations
            if ids == id_needed:
                corner1_x = aruco_box[0][0] # Top left x value
                corner2_x = aruco_box[2][0] # Bottom right x value
                print("loc")
                print(corner1_x)
               # time.sleep(1)
                distance = 0.0
                if corner1_x > 340:
                    distance = corner1_x - 340
                    print("distance")
                    print(distance)
                    cv2.putText(frame, f"distance: {distance}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                1, (255, 255, 255), 2, cv2.LINE_AA)


                if corner1_x < 335:
                    distance = 335 - corner1_x
                    print("distance")
                    print(distance)
                    cv2.putText(frame, f"distance: {distance}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                1, (255, 255, 255), 2, cv2.LINE_AA)
                    
                if corner1_x > 334 and corner1_x < 340:
                    distance = 0
                    print("distance")
                    print(distance)
                    cv2.putText(frame, f"distance: {distance}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                1, (255, 255, 255), 2, cv2.LINE_AA)
                    
            
                #pixel value around 297 get it to equal there
 
            #   distance1 = corner1_x - 


            intersection_area = cv2.contourArea(cv2.convexHull(np.concatenate([middle_box, aruco_box])))
            union_area = box_size**2 + cv2.contourArea(cv2.convexHull(aruco_box)) - intersection_area
            if union_area == 0:
                union_area = 0.01
            overlap_ratio = intersection_area / union_area
            # print(overlap_ratio)

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

    cv2.imshow("Camera live stream", frame)

    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()