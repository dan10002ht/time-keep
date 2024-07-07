# main.py
import multiprocessing
import multiprocessing.queues
import threading
from Fingerprint_Process.Finger_Runnable import Process_finger, Change_Flag_Finger
from Fingerprint_Process.service_finger import finger
from Face_Recognition.face_recogRunnable import thread_service
import time
import RPi.GPIO as GPIO
from  GUI.gui import WebcamApp
import tkinter as tk
from service import APIClient
import os 
import cv2
import json 

URL = "https://datn-alpha.vercel.app/api/"
authorized_token = None
user_name = "danlaanh202"
password = "danlaanh202"
user_ID = None
button_pin = 26
job_flag = 0

BUZZER_PIN = 17
LED_PIN = 27

def callback_regFaceID(frame):
    global queue_finger
    thread_face = threading.Thread(target=thread_service, args=(queue_finger,frame,))
    thread_face.start()
def str_2json(json_string):
    try:
        # Convert string to JSON (Python dictionary)
        json_object = json.loads(json_string)
        print(json_object)
        return json_object
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)

def find_user_id(finger_id, face_id):
    file_path = "/home/pi/Smart_lock/user_mapping.json"
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            
            # Iterate through the list of dictionaries
            for entry in data:
                if entry['Finger_ID'] == finger_id and entry['Face_ID'] == face_id:
                    return entry['userID']
        
        return None  # Return None if no match is found
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return None   

def button_callback(channel,flag1, flag2):
    print(channel)
    if(channel == 26 and GPIO.input(button_pin) == 0):
        print("Finger request!!!")
        print(GPIO.input(button_pin))
        flag1.value = 1
        flag2.value = 1       

def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")

def submit_toServer(Timestamp_str, ID):
    user_ID = find_user_id(str(ID["finger_id"]),str(ID["face_id"]) )
    str_folder = Timestamp_str.strftime("%d_%m_%Y")
    str_file_timestamp = Timestamp_str.strftime("%H_%M_%S")
    current_dir = os.path.dirname(os.path.realpath(__file__))
    ensure_folder_exists(current_dir + '/datacheckin/'+ str(str_folder))
    image_path = current_dir + '/datacheckin/'+ str(str_folder)+ f"/{user_ID}_{str_file_timestamp}.jpg"
    print(image_path)
    img = cv2.imread("/home/pi/Smart_lock/Face_Recognition/recog.jpg")
    cv2.imwrite(image_path, img)
    resp = Client.reuquest_checkin(img, user_ID)
    print(resp.text)
    resp = str_2json(resp.text)
    if(resp["success"]):
        buzzer_thread = threading.Thread(target=bip_bip_success)
        buzzer_thread.start()
        return True
    else:
        bip_bip_fail()
        return False

def start_server(queue, flag_Finger):
    server_proc = threading.Thread(target=Process_finger, args=(queue,flag_Finger,))
    server_proc.start()
    return server_proc

def thread_readQueue(queue:multiprocessing.Queue):
    prev_time = 0
    while True:
        if time.time()*1000 - prev_time >= 1000:
            if not queue.empty():
                obj = queue.get()
                print(f"obj_type:{type(obj)}, object value:{obj}")
                if(obj["obj_type"] == 0):
                    app.update_finger_sensor(obj)
                if(obj["obj_type"] == 1):
                    print(obj)
                    app.update_face_id(obj)
            else:
                pass
            prev_time = time.time()*1000
        time.sleep(0.1)

def bip_bip_success():
    GPIO.output(LED_PIN, GPIO.HIGH)
    for _ in range(2):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn on the buzzer
        time.sleep(0.5)                     # Wait for 0.5 seconds
        GPIO.output(BUZZER_PIN, GPIO.LOW)   # Turn off the buzzer
        time.sleep(0.1)                     # Wait for 0.1 seconds
    time.sleep(1)
    GPIO.output(LED_PIN, GPIO.LOW)

def bip_bip_fail():
    for _ in range(2):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn on the buzzer
        time.sleep(0.1)                     # Wait for 0.1 seconds
        GPIO.output(BUZZER_PIN, GPIO.LOW)   # Turn off the buzzer
        time.sleep(0.1)                     # Wait for 0.1 seconds

if __name__ == "__main__":
    Client =  APIClient(URL)
    Client.login(endpoint="login",username="danlaanh202", password="danlaanh202")
    GPIO.setmode(GPIO.BCM)  # or GPIO.BOARD
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Set up the LED pin as an output
    GPIO.setup(LED_PIN, GPIO.OUT)
    # Set up the buzzer pin as an output
    GPIO.setup(BUZZER_PIN, GPIO.OUT)

    flagFinger = multiprocessing.Value('i', 0)
    flagimage = multiprocessing.Value('i', 0)
    GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=lambda channel: button_callback(channel, flagFinger, flagimage), bouncetime=300)
    root = tk.Tk()
    app = WebcamApp(root)
    app.register_callback_genFaceID(callback_thread_genFaceID=callback_regFaceID)
    app.register_callback_submit(submit_toServer)
    app.register_buzzer_error(bip_bip_fail)
    #start a queue
    queue_finger = multiprocessing.Queue()

    # Start the server process
    server_proc = start_server(queue_finger, flagFinger)
    
    # Start queue read Finger:
    Thread_ReadQueue = threading.Thread(target=thread_readQueue, args=(queue_finger,))
    Thread_ReadQueue.start()
    root.mainloop()

    # # Stop the server
    try:
        
        server_proc.join()
        # Thread_ReadQueue.join()
    except KeyboardInterrupt:
        server_proc.terminate()
        server_proc.join()
    finally:
        print("Main: All processes have been terminated.")