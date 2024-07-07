
from function import *
import cv2
import os

cap = cv2.VideoCapture(0)

if not cap.isOpened():
     print("Error: Could not open webcam.")
     exit()

try:
    
    # Display the frame
    ret, frame = cap.read()
    cv2.imshow('Webcam', frame)
    while True:
        ret, frame = cap.read()
        if not ret:
             print("Failed to capture image")
             break
        try:
            start_time = time.time()
            print("\nstart face recognition")
            imgs_path = face_detection(frame)
            print(imgs_path)
            if imgs_path == None:
                #os.remove(imgs_path)
                print('Please try again')
                break
            else:
                name = recognition(image_path = imgs_path)
                img = cv2.imread(imgs_path)
                cv2.putText(img, name, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                cv2.imwrite('./recog1.jpg'.format(name), img)
                # os.remove(imgs_path)
                end_time = time.time()
                print(f"\n\nTotal time: {(end_time - start_time):.3f} seconds\n")
                print('Finish')
                break
        except Exception as e:
            print(e)
            continue
        
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Release the webcam and close all windows
    # cap.release()
    cv2.destroyAllWindows()