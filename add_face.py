# This program will take a specified number of pictures of a person and store it.

# Import Libraries
import cv2
import os
import time
import numpy as np
import platform
import pymongo
import io
import matplotlib.pyplot as plt
from bson.binary import Binary
from PIL import Image

if platform.system() == "Windows" or platform.system() == "Darwin":
    from PIL import ImageGrab  # WINDOWS/MAC
else:
    import pyscreenshot as ImageGrab  # LINUX

width, height = (1600, 900)

count = 0


def mongodb_con(pic_nb):
    print("connecting to database...")
    client = pymongo.MongoClient(
        "mongodb://m001-student:Password@cluster0-shard-00-00.nvnbz.mongodb.net:27017/Positive?ssl=true&replicaSet"
        "=atlas-qi9ptr-shard-0&authSource=admin&retryWrites=true&w=majority")  # open connection to mongo db to save
    # face to database
    face_database = client["face_detection"]  # select database
    faces_collection = face_database["faces"]  # select collection
    img_path = directory + "/" + str(pic_nb) + ".png"
    # return face_database,faces_collection
    print("connected to Mongodb")

    im = Image.open(img_path)
    image_bytes = io.BytesIO()
    im.save(image_bytes, format='PNG')
    image = {
        'data': image_bytes.getvalue()
    }

    faces_collection.insert_one(image).inserted_id
    print("image " + str(pic_nb) + ".png has been inserted")
    os.remove(img_path)


def input_method():
    face_input = input("Record from screen or webcam: ").lower()
    if "screen" in face_input or "display" in face_input:
        return "screen"
    elif "cam" in face_input:
        return "webcam"
    else:
        return input_method()


def process_frame(frame):
    global count

    # Convert to grayscale (black and white)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Finding Faces
    faces = face_cascade.detectMultiScale(gray)

    num_faces = len(faces)

    # Give Message if No Faces are Detected
    if num_faces == 0:
        text1 = "No Face Detected!"
        text2 = "Please make sure " + name + " is in frame."
        cv2.putText(frame, text1, (0, 20), font, font_size, red, 2, cv2.LINE_AA)
        cv2.putText(frame, text2, (0, 40), font, font_size, red, 2, cv2.LINE_AA)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + h]

        # Give Message and Pause Data Collection if Multiple Faces are Detected
        if num_faces == 1:
            count += 1
            file = directory + "/" + str(count) + ".png"
            cv2.imwrite(file, roi_color)
            mongodb_con(count)
        else:
            text1 = str(num_faces) + " Faces Detected! Data Collection Paused."
            text2 = "Please make sure only " + name + " is in frame."
            cv2.putText(frame, text1, (0, 20), font, font_size, red, 2, cv2.LINE_AA)
            cv2.putText(frame, text2, (0, 40), font, font_size, red, 2, cv2.LINE_AA)

        # Display count
        text = str(count) + "/" + str(num_pics)
        cv2.putText(frame, text, (x, y), font, font_size, white, 2, cv2.LINE_AA)

        # Draw Rectangle around face
        x_end = x + w
        y_end = y + h
        cv2.rectangle(frame, (x, y), (x_end, y_end), cyan, 3)
    return frame


name = input("Enter your name: ").title()
directory = name.replace(" ", "-")
directory = "../Images/" + directory

try:
    os.mkdir(directory)
except FileExistsError:
    print("The folder %s already exists! Overwriting." % directory)
else:
    print("Succesfully created folder %s!" % directory)

input = input_method()
start_time = time.time()

# Specify the Classifier for the Cascade
face_cascade = cv2.CascadeClassifier('./Cascades/data/haarcascade_frontalface_default.xml')

# Start Capturing Video from Default Webcam
webcam_capture = cv2.VideoCapture(0)

# number of picture to be taken by the camera
num_pics = 3

font = cv2.FONT_HERSHEY_SIMPLEX
font_size = 0.75
white = (255, 255, 255)
cyan = (255, 255, 0)
red = (0, 0, 255)

while (True):
    # Capture frame-by-frame
    if input == "screen":
        screen_pil = ImageGrab.grab(bbox=(0, 0, width, height))
        screen_np = np.array(screen_pil)
        frame = cv2.resize(cv2.cvtColor(screen_np, cv2.COLOR_BGR2RGB), (int(width / 1.5), int(height / 1.5)))
    else:
        ret, frame = webcam_capture.read()

    processed_frame = process_frame(frame)
    # processed_screen = cv2.resize(processed_screen_full, dsize=(800, 450), interpolation=cv2.INTER_LINEAR)

    # Display the resulting frame
    cv2.imshow(input.title(), processed_frame)

    # Stop if user presses 'q' or specified numebr of pictures have been taken
    if (cv2.waitKey(20) & 0xFF == ord('q')) or count >= num_pics:
        break

# Stop getting webcam input and close all windows at the end of the program
webcam_capture.release()
cv2.destroyAllWindows()

if count >= num_pics:
    print("Face Data Collection Complete")
    end_time = time.time()
    total_time = end_time - start_time
    print("Program complete in %f seconds" % total_time)
else:
    print("Cancelled")
