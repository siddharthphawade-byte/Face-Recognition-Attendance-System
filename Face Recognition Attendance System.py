import cv2
import face_recognition
import numpy as np
import csv
import os
from datetime import datetime

# --- 1. Load Known Faces ---
path = 'known_faces'
images = []
classNames = []
myList = os.listdir(path)

print("Loading known faces...")
for cl in myList:
    # Read the image
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    # Extract the name from the filename (e.g., "elon_musk.jpg" -> "elon_musk")
    classNames.append(os.path.splitext(cl)[0])

# Function to encode all loaded images
def findEncodings(images):
    encodeList = []
    for img in images:
        # Convert to RGB (face_recognition uses RGB, OpenCV uses BGR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Find the encoding for the first face found in the image
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)
print(f"Encoding Complete. Loaded {len(encodeListKnown)} faces.")

# --- 2. Create Attendance Logging Function ---
def markAttendance(name):
    with open('attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        
        # Only log them if they haven't been logged yet today
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            dateString = now.strftime('%Y-%m-%d')
            f.writelines(f'\n{name},{dtString},{dateString}')

# --- 3. Initialize Webcam and Run Recognition ---
cap = cv2.VideoCapture(0) # 0 is usually the default laptop webcam

while True:
    success, img = cap.read()
    # Resize image to 1/4 size for faster processing
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Find all faces and their encodings in the current frame
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        # Compare current face to known faces
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        
        # Find the lowest distance (best match)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            
            # Scale face locations back up to original size
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            
            # Draw a box around the face
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            
            # Write the name
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            
            # Log the attendance
            markAttendance(name)

    # Display the resulting image
    cv2.imshow('Face Recognition Attendance', img)
    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()