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

cap = cv2.VideoCapture(0)

def center_point(x,y,w,h):
    return inner_point((x,y,w,h), 0.5, 0.5)

def lerped(start, end, percentage):
    return (percentage * end) + ((1-percentage) * start)

def inner_point(rect, x_percent, y_percent):
    x,y,w,h = rect
    print("Finding Inner Point of: {}, {}".format(y, y+h))
    x_val = int(lerped(x, x+w, x_percent))
    y_val = int(lerped(y, y+h, y_percent))
    return (x_val, y_val)

all_start = time.time()
frame_count = 0
while 1:
    start = time.time()
    ret, img = cap.read()
    frame_count += 1

    # img.shape is heightxwidth
    print("Image: {}x{}".format(img.shape[1], img.shape[0]))
    # img = cv2.resize(img,(640,480),interpolation=cv2.INTER_AREA)
    # img = cv2.resize(img,(0,0),fx=0.75, fy=0.75, interpolation=cv2.INTER_AREA)
    # img = cv2.resize(img,(0,0),fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    # print("Resized: {}x{}".format(resized.shape[1], resized.shape[0]))

    # import pdb; pdb.set_trace()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    face_found = False
    eyes_found = False

    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        between_eyes = inner_point((x,y,w,h), 0.5, 0.4)
        print("Between Eyes: {}".format(between_eyes))
        cv2.circle(img, between_eyes, 10, (0,0,0), 8)
        face_found = True
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

        eyes = eye_cascade.detectMultiScale(roi_gray,1.3,20)
        if len(eyes) > 0:
            eyes_found = True
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
            eye_center = center_point(ex,ey,ew,eh)
            print("Eye Center: {}".format(eye_center))
            cv2.circle(roi_color, eye_center, 5, (255,255,255), 4)

    if len(faces) == 0:
        profile_faces = profile_face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in profile_faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
            cv2.circle(img, inner_point((x,y,w,h), 0.5, 0.4), 10, (0,0,0), 8)
            face_found = True

    print("Frame processing took {} seconds".format(time.time() - start))
    print("Face Found: {}. Eyes Found: {}".format(face_found, eyes_found))

    cv2.imshow('img',img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

    # Just to limit CPU usage
    # time.sleep(1)

    print("Processed {0} frames in {1:0.2f} seconds".format(frame_count, time.time() - all_start))

cap.release()
cv2.destroyAllWindows()
