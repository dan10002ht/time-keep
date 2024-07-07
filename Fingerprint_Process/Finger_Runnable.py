import multiprocessing
from .service_finger import finger
import time
import threading
from datetime import datetime
import os


JOB_FREE = 0
JOB_BUSY = 1
JOB_DONE = 2
JOB_ERROR = 3

MODE_RUN_NORMAL  = 0
MODE_RUN_ADMIN = 1

button_pin = 26         # replace with your GPIO pin number
Finger_service = finger()
prev_status  = -1

JOB_Status = JOB_FREE
previos_FingerID = -1
job_Flag_Finger = 0

PATH_SAVE_IMAGE = "/home/pi/Pictures/Finger_Image"

# Add event detection with debounce time
def Change_Flag_Finger():
    global job_Flag_Finger
    job_Flag_Finger = 1
    print("Job Flag:",job_Flag_Finger)

def Enqueue(queue:multiprocessing.Queue, obj_queue):
    
    try:
        queue.put(obj_queue)
        print("----- queue put sucess!!")
        return True
    except:
        print("-------- queue put fail!!")
        return False
def thread_save_finger(FingerID, time_stamp, url_path):
    global JOB_Status
    if(JOB_Status == JOB_FREE):
        JOB_Status = JOB_BUSY
        file_name = url_path + "/" + str(FingerID) +"_"+ str(time_stamp) + "_Finger.bmp"
        print(file_name)
        res = Finger_service.Service_Download_Image(file_destination = file_name)
        if(res == 0):
            print("Save success")
        else:
            print("Save error")
        JOB_Status = JOB_FREE
        
def thread_read_finger(queue, run_mode, flag_process, GPIO_OBJ = None):
    global previos_FingerID
    global job_Flag_Finger
    global JOB_Status
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_dir, 'dataset.json')
    while(True):
        if(run_mode == MODE_RUN_NORMAL  and JOB_Status == JOB_FREE):
            if(flag_process.value == 1):
                print("Enter job")
                time.sleep(2) #delay 2s
                print('Begin read finger')
                start_time = time.time()
                JOB_Status = JOB_BUSY
                obj = {"Result":{"status":0, 'Data':{"ID": -1, "accept": False, "role": -1}}, "obj_type":0 }
                obj["Result"] = Finger_service.Service_ScanFinger()
                JOB_Status = JOB_FREE
                if(obj["Result"]["status"] == 1):
                    if(True):
                        previos_FingerID = obj["Result"]["Data"]["ID"]
                        obj["Timestamp"] = int(time.mktime(datetime.now().timetuple()))
                        print("Oject send:",obj)
                        Enqueue(queue,obj)
                        # thread_save_finger(obj["Result"]["Data"]["ID"],obj["Timestamp"],PATH_SAVE_IMAGE)
                        end_time = time.time()
                        print(f"\n\nTotal time: {(end_time - start_time):.3f} seconds\n")
                        print(obj)
                flag_process.value = 0
        time.sleep(0.2)


def Process_finger(queue, flag_process, request_Upper = None ,Notifi_CallBack = None):
    finger_read_service = threading.Thread(target = thread_read_finger, args=(queue, MODE_RUN_NORMAL,flag_process, ))
    finger_read_service.start()
    finger_read_service.join()







