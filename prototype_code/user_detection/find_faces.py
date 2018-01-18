# FROM https://pythonprogramming.net/haar-cascade-face-eye-detection-python-opencv-tutorial/

import numpy as np
import cv2
import time

# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades

#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
# https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
# https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye.xml
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

profile_face_cascade = cv2.CascadeClassifier('haarcascade_profileface.xml')

cap = cv2.VideoCapture(1)

while 1:
    start = time.time()
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    face_found = False
    eyes_found = False

    for (x,y,w,h) in faces:
        # cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        face_found = True
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

        eyes = eye_cascade.detectMultiScale(roi_gray,1.3,20)
        if len(eyes) > 0:
            eyes_found = True
        # for (ex,ey,ew,eh) in eyes:
        #     cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

    if len(faces) == 0:
        profile_faces = profile_face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in profile_faces:
            # cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
            face_found = True


    print("Frame processing took {} seconds".format(time.time() - start))
    print("Face Found: {}. Eyes Found: {}".format(face_found, eyes_found))

    # cv2.imshow('img',img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

    # Just to limit CPU usage
    time.sleep(1)

cap.release()
cv2.destroyAllWindows()
