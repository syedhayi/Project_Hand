import mediapipe as mp
import cv2
import time
import math
import numpy as np


class handDetectors():
    def __init__(self, mode = False, maxHands = 2, detectionCon = 0.5, trackCon = 0.5 ):
        self.mode = mode
        self.maxHands = maxHands
        self.detectCon = detectionCon
        self.tackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode,self.maxHands,
                                        self.detectCon , self.tackCon)
        self.mpDraw = mp.solutions.drawing_utils
    def findHands(self, img, draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        #print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS,self.mpDraw.DrawingSpec(color= (0, 0, 0)))

        return img

    def findPosition(self, img, handNo = 0, draw = True):
        lmList = []


        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            #print(self.results.multi_handedness)
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                #print(id, cx, cy)
                lmList.append([id, cx, cy])
                #id_.append(id)
                if draw:
                    cv2.circle(img, (cx,cy), 5, (255,0,0), cv2.FILLED)

        # if self.results.multi_handedness:
        #     for idx, classification in enumerate(self.results.multi_handedness):
        #         #print(classification.classification[0].label)
        #         label.append(classification.classification[0].label)
                #print(label)
        # if self.results.multi_handedness[0] is None:
        #     pass
        # #if len(self.results.multi_handedness) != 0:
        # else:
        #     print(self.results.multi_handedness[0].classification[0].label)

        return lmList

    def get_label(self):
        label = []


        if self.results.multi_handedness:
            for idx, classification in enumerate(self.results.multi_handedness):

                label.append(classification.classification[0].label)
                #print((classification.classification[0].label).dtype)
                # print(self.results.multi_hand_landmarks[self.mpHands.HandLandmark.WRIST].x)
        return label

    def get_angle(self,img,  joint_list):
        angle1 = []
        for hand in self.results.multi_hand_landmarks:
            for joint in joint_list:
                a = np.array([hand.landmark[joint[0]].x, hand.landmark[joint[0]].y])
                b = np.array([hand.landmark[joint[1]].x, hand.landmark[joint[1]].y])
                c = np.array([hand.landmark[joint[2]].x, hand.landmark[joint[2]].y])

                radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
                angle = np.abs(math.degrees(radians))

                #angle = np.abs((radians*180/np.pi).astype(int))
                if angle > 180.0:
                    angle = 360 - angle
                angle1.append(int(angle))

                # angle.append(angle)
                cv2.putText(img, str(round(angle, 2)), tuple(np.multiply(b, [640, 480]).astype(int)),cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 0, 0), 2)

        return angle1




def main():
    pTime = 0  # previous time
    cTime = 0  # current time
    cap = cv2.VideoCapture(1)     ## 640 x 480 resolution
    detector = handDetectors()
    while 1:
        ret, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.findHands(img)

        lmList = detector.findPosition(img)
        #if len(lmList) != 0:
            #print(lmList[4])
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2,
                    (255, 0, 255), 3)
        cv2.imshow('frame', img)

        if cv2.waitKey(10) == ord(' '):
            break


    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    main()