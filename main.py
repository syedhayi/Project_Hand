import Hand_Tracking as htm
import cv2
import time
import math
import socket

def remap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#connect to the same host ip and port as the server
host = '192.168.xx.xx'     ##change it to your router ip which is connected to the server
port = 8888

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    width, height = 640, 480
    cap = cv2.VideoCapture(1)  ## 640 x 480 resolution
    cap.set(3, width)
    cap.set(4, height)
    pTime = 0  # previous time
    cTime = 0  # current time
    detector = htm.handDetectors(maxHands=1, detectionCon=0.8)
    pwm = 0

    while 1:
        ret, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.findHands(img, draw=True)
        lmList = detector.findPosition(img, draw=False)
        label = detector.get_label()

        if len(label) != 0:
            if len(lmList) != 0:
                coord_ = lmList[0][1], lmList[0][2]
                if label[0] == 'Left':
                    # print(lmList[4])
                    x1, y1 = lmList[4][1], lmList[4][2]
                    x2, y2 = lmList[8][1], lmList[8][2]

                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    cv2.circle(img, (x1, y1), 5, (255, 0, 0), cv2.FILLED)
                    cv2.circle(img, (x2, y2), 5, (255, 0, 0), cv2.FILLED)
                    # image = cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    length = math.hypot(x2 - x1, y2 - y1)

                    if length < 25:
                        cv2.circle(img, (cx, cy), 5, (0, 0, 0), cv2.FILLED)
                    else:
                        pwm = int(remap(length, 25, 210, 0, 255))
                    cv2.putText(img, label[0], coord_, cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (255, 0, 0), 2)
                    joint_ = [[4,3,2], [7,6,5], [11, 10, 9],  [15, 14, 13],  [19, 18, 17]]      ## joint list of the angle wanted to calculate ## [A ,B, C] -> to get angle of line AB and BC
                    angle = detector.get_angle(img, joint_)                                     ## returns the angle of B in ([A, B, C]), for all specified joints
                    print(angle)
                    angle1 = remap(angle[0], 80, 176, 0, 177)
                    s.sendall(str.encode(
                    str(abs(180 - int (angle1))) + ',' + str(abs(180 -angle[1])) + ',' +
                    str(abs(180 -angle[2])) + ',' + str(abs(180 -angle[3])) + ',' + str(abs(177 -angle[4])) + ',' + ';'))

                # Since my 3d model is left hand i don't want to override the left hand angles with the right
                # so the calculation and sending values only will work with Left hand
                # When it's Right hand, display message to try Left hand
                elif label[0] == 'Right':
                    text_offset = 30
                    cv2.putText(img, 'Try your Left Hand', (coord_[0] + 60, coord_[1] + 60),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (255, 0, 0), 3)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 0, 0), 2)
        cv2.imshow('frame', img)
        if cv2.waitKey(10) == ord(' '):
            break

    cv2.destroyAllWindows()
    cap.release()
s.close()