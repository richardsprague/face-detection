import numpy as np
import cv2

cap = cv2.VideoCapture(0)

while (True):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    r = 1000.0 / gray.shape[1]
    dim = (1000, int(gray.shape[0] * r))

        # perform the actual resizing of the image and show it

    cropped = gray[70:170, 440:540]
    resized = cv2.resize(cropped, dim, interpolation=cv2.INTER_AREA)
    cv2.imshow("resized", resized)

cap.release()
cv2.destroyAllWindows()

