import cv2
import statistics

draw=False
drawEyes=True

#Blue, green, Red


# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
# To capture video from webcam. 
cap = cv2.VideoCapture(0)


# To use a video file as input
# cap = cv2.VideoCapture('filename.mp4')

def findFaces(img: cv2) -> list:
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect the faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    eyes = eye_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) > 0 and len(eyes) > 0:
        # Draw the rectangle around each face
        realFace = []
        biggestArea = [0, 0]
        n = 0
        for (x, y, w, h) in faces:
            if biggestArea[0] < w * h:
                biggestArea = [w * h, n]
            n += 1
        realFace = faces[biggestArea[1]]
        if draw:
            cv2.rectangle(img, (realFace[0], realFace[1]), (realFace[0] + realFace[2], realFace[1] + realFace[3]),
                          (255, 0, 0), 2)
        #     cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        realEyes = []
        n = 0
        for (x2, y2, w2, h2) in eyes:
            # if x2<realFace[0]+realFace[2] and x2>realFace[0] and y2<realFace[1]+realFace[3] and y2>realFace[1]:
            if x2 < realFace[0] + realFace[2] and x2 > realFace[0] and realFace[1] + realFace[3] / 2 > y2 > realFace[
                1] + realFace[3] / 6:
                #            cv2.rectangle(img, (x2, y2), (x2+w2, y2+h2), (0, 255, 0) , 2)
                realEyes += [eyes[n]]

            n += 1


        n = 0
        veryRealEyes = []
        tolerance = realFace[3] / 30

        for (x, y, w, h) in realEyes:
            count = 0
            for (x2, y2, w2, h2) in realEyes:
                if y + tolerance > y2 > y - tolerance:
                    count += 1
            if count > 1:
                veryRealEyes += [n]
            n += 1
        if len(veryRealEyes) > 0:
            eyes = []
            for i in veryRealEyes:
                eyes += [realEyes[i]]
            if draw:
                cv2.circle(img, (10, 10), 20, (0, 255, 0), 2)
        else:
            if draw:
                cv2.circle(img, (10, 10), 20, (0, 0, 255), 2)
            eyes = realEyes

        for (x2, y2, w2, h2) in eyes:
            y2 += int(h2 / 4)
            h2 = int(h2 / 2)
            if draw:
                cv2.rectangle(img, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)




        faces = realFace
        #    eyes=realEyes

        return faces, eyes
    return [[], []]


def run_face_detection():
    'Keep running the face detection until the ESC key is pressed.'
    frames = 0
    center=[]
    left=[]
    right=[]
    calibration = 1
    calibrationTime = 20
    calibrationCounter = calibrationTime

    while frames < 1000:
        frames += 1
        # Read the frame
        frame, img = cap.read()

        # get faces and eyes
        faces, eyes = findFaces(img)
        if len(faces) > 0 and len(eyes) > 0:

            # height = img.shape[1]
            # width = img.shape[0]

            difs = []
            for (startx, starty, w, h) in eyes:

                n = 0
                totalList = [0] * w

                x = int(startx)  # +w/4)
                total = 0
                while x < startx + w:  # + 3 * w / 4 :
                    y = starty + int(h / 3)
                    oldTotal = int(total / 3 / h)
                    totalList[n] = oldTotal
                    n += 1

                    total = 0
                    while y < starty + 2 * h / 3:
                        total += sum(img[y, x])

                        y += 1
                    x += 1

                totalList[0] = totalList[1]

                small = min(totalList)
                large = max(totalList)
                x = startx
                maxAverages = [255] * 10
                darkest = [2550, 0]
                n = 0
                for i in totalList:
                    x += 1
                    i = (i - small) / (large - small) * 255
                    maxAverages[n] = i
                    n = (n + 1) % 10
                    if sum(maxAverages) < darkest[0]:
                        darkest = [sum(maxAverages), x - 5]
                    img[y, x] = [i, i, i]

                img[y, darkest[1]] = [0, 255, 0]

                if draw:
                    cv2.circle(img, (darkest[1], starty + int(h / 2)), 10, (0, 255, 0), 2)
                if draw:
                    cv2.circle(img, (startx + int(w / 2), starty + int(h / 2)), 10, (0, 0, 255), 2)
                difs += [startx + int(w / 2) - darkest[1]]

         #   print(sum(difs)/len(difs))
            eyeDirection = sum(difs) / len(difs)
        #    print(faces)
            faceCenter=faces[0] + int(faces[2] / 2)
            if calibration<4:
                calibrationCounter -= 1

                if calibrationCounter < 0:
                    calibrationCounter = calibrationTime
                    print("Test #", calibration, "Done: mean", sum(center) / len(center), "std", statistics.stdev(center))
                    calibration += 1
                    if calibration==4:
                        leftAve=sum(left) / len(left)
                        rightAve=sum(right) / len(right)
                        centerAve=sum(center) / len(center)
                        magnitude_change = 700/(rightAve-leftAve)

                elif calibration==3: #look left
                    left+=[eyeDirection]
                    cv2.rectangle(img, (faceCenter-300, 350), (faceCenter-400, 450), (0, 255, 0),2) # Calibration spot

                elif calibration==2: #look right
                    cv2.rectangle(img, (faceCenter+300, 350), (faceCenter+400, 450), (0, 255, 0), 2)  # Calibration spot
                    right += [eyeDirection]

                elif calibration == 1:
                    cv2.rectangle(img, (faceCenter-50, 350), (faceCenter+50, 450), (0, 255, 0), 2)  # Calibration spot
                    center += [eyeDirection]

            elif draw:
                cv2.circle(img, (int(faceCenter+(eyeDirection - centerAve) * magnitude_change), 400), 50, (0, 255, 255), 2)  # exact spot

            eyes1 = eyes[0]

            if drawEyes:
                x=eyes1[1]
                while x<eyes1[1] + eyes1[3]:
                    y=eyes1[0]
                    prevColor=0
                    while y < eyes1[0] + eyes1[2]:

                   #     newColor=int(img[x, y][2]/(sum(img[x,y])+1))
                        newColor = int(sum(img[x, y])/3)
                        img[x, y] = [abs(newColor - prevColor), abs(newColor - prevColor), abs(newColor - prevColor)]
                #        img[x,y] = [abs(newColor-img[x, y][0]), abs(newColor-img[x, y][1]), abs(newColor-img[x, y][2])]
                        y+=1
                        prevColor=newColor*2
                    x+=1

                cropped = img[eyes1[1]:eyes1[1] + eyes1[3], eyes1[0]:eyes1[0] + eyes1[2]]

                if cropped.shape[0] > 0:
                    r = 1000
                    dim = (1000, 1000)  # int(img.shape[0] * r))
                    resized = cv2.resize(cropped, dim, interpolation=cv2.INTER_AREA)
                    cv2.imshow("resized", resized)

        # Display
        # if not drawEyes:
        cv2.imshow('img', img)
        # Stop if escape key is pressed
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break


run_face_detection()

# Release the VideoCapture object
cap.release()