import math
import time
import cv2
import mediapipe as mp
import numpy as np
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


wCam, hCam = 640, 480
pTime = 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    # print(lmList)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.circle(img, (x1, y1), 10, (255, 50, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 50, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 50, 0), 2)
        cv2.circle(img, (cx, cy), 10, (255, 50, 0), cv2.FILLED)
        length = math.hypot(x2-x1, y2-y1)
        # print(length)

        vol = np.interp(length, [50, 300], [minVol, maxVol])
        viewVol = np.interp(length, [50, 300], [400, 150])
        # print(viewVol)
        volume.SetMasterVolumeLevel(vol, None)
        cv2.rectangle(img, (50, 150), (80, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(viewVol)), (80, 400), (0, 255, 0), cv2.FILLED)

        if length < 50:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

    cTime = time.time()
    fps1 = 1/(cTime-pTime)
    fps = int(fps1)
    pTime = cTime
    cv2.putText(img, (str("FPS: ") + str(fps)), (490, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 4)

    cv2.imshow("Feed", img)
    cv2.waitKey(1)
