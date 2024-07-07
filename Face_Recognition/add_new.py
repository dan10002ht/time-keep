from function import add_new_member, face_detection
import cv2
import os

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break
        
        # Display the frame
        cv2.imshow('Webcam', frame)
        try:
            imgs_path = face_detection(frame)
            print("-------------------")
            if imgs_path == None:
                #os.remove(imgs_path)
                print('Please try again')
            else:
                print('Enter userId: ')
                userId = input()
                print('userId: ', userId)


                img = cv2.imread(imgs_path)
                add_new_member(img,userId)
                #os.remove(imgs_path)
                print('Finish')
                break
        except Exception as e:
            continue
        
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Release the webcam and close all windows
    cap.release()
    cv2.destroyAllWindows()