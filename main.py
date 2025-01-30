import cv2 as cv
import numpy as np
import math
import serial
import time
import threading

serialDevice = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)

CHANGE_COMMAND = 'C'

cap = cv.VideoCapture(2)

low_green = np.array([50, 50, 50])
high_green = np.array([75, 255, 255])

low_red = np.array([170, 70, 50])
high_red = np.array([180, 255, 255])

collision_detected = False
command_sent = False


def send_change_command(): #send command to arduino when collision detected
    global collision_detected, command_sent
    if not command_sent:
        serialDevice.write(CHANGE_COMMAND.encode('utf-8'))
        print('Change Command sent!')
        command_sent = True

        start_time = time.time()

        while time.time() - start_time < 3:
            if serialDevice.in_waiting > 0:
                ack = serialDevice.readline().decode('utf-8').strip()
                print(f"Arduino: {ack}")
                if ack == "OK":
                    time.sleep(2)
                    collision_detected = False
                    break
    else:
        print("Command already sent, waiting for Arduino to process.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    green_mask = cv.inRange(hsv_frame, low_green, high_green)
    red_mask = cv.inRange(hsv_frame, low_red, high_red)

    green_contours, _ = cv.findContours(green_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    red_contours, _ = cv.findContours(red_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    red_corners = []

    for contour in red_contours: #detecting the red object and add the corners of the object to array
        area = cv.contourArea(contour)
        if area > 100:
            rect = cv.minAreaRect(contour)
            box = cv.boxPoints(rect)
            box = np.intp(box)
            cv.drawContours(frame, [box], 0, (0, 0, 255), 2)
            red_corners.extend(box)

            x, y, w, h = cv.boundingRect(contour)
            cv.putText(frame, 'Red object', (x, y - 10), cv.FONT_ITALIC, 1, (0, 0, 255), 2)

    for contour in green_contours: #detecting the green object and calculate the distance between green objects and red object
        area = cv.contourArea(contour)
        if area > 1000:
            M = cv.moments(contour)
            x, y, w, h = cv.boundingRect(contour)
            cx, cy = x + w // 2, y + h // 2

            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            collision = False
            for corner in red_corners:
                distance = math.sqrt((cx - corner[0]) ** 2 + (cy - corner[1]) ** 2)
                if distance <65:
                    collision = True
                    if not collision_detected:
                        collision_detected = True
                        threading.Thread(target=send_change_command).start()
                    break

            if collision:
                cv.putText(frame, 'Collision!', (x, y - 20), cv.FONT_ITALIC, 1, (0, 0, 255), 2)
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
            else:
                command_sent = False

    # Display frame
    cv.imshow('Live', frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
