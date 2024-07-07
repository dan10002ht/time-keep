from Face_Recognition.function import *
import multiprocessing
import cv2
import time
def Enqueue(queue:multiprocessing.Queue, obj_queue):
    
    try:
        queue.put(obj_queue)
        print("----- queue put sucess!!")
        return True
    except:
        print("-------- queue put fail!!")
        return False
    
def thread_service(queue:multiprocessing.Queue, frame_image):
    obj = {"obj_type":1,"Result":{"ID": -1}, "Status":0, "Message":""}
    time_start = time.time()*1000
    while(time.time()*1000 - time_start <= 5000):
        try:
            print('\nStart Face time keeping')
            start_time = time.time()
            imgs_path = face_detection(frame_image)
            
            if imgs_path == None:
                print('Please try again')
                obj["Message"] = "Please try to check Face again!"
            else:
                user_ID = recognition(image_path = imgs_path)
                print(user_ID)
                print('Finish')
                print(f"\n\nTotal time: {(time.time() - start_time):.3f} seconds\n")
                obj["Result"]["ID"] = user_ID
                obj["Status"] = 1
                obj["Message"] = "Done!"
                break
        except Exception as e:
            obj["Message"] = "Error"
            print(f"Error in {e}")
        time.sleep(0.1)

    Enqueue(queue=queue, obj_queue=obj)