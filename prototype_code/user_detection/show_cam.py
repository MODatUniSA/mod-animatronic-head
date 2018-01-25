import numpy as np
import cv2

cap = cv2.VideoCapture(1)

while(True):
    ret, frame = cap.read()
    h_flip=cv2.flip(frame,1)
    gray = cv2.cvtColor(h_flip, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
