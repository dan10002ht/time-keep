# client.py
import multiprocessing
from multiprocessing.connection import Client
import time
import threading 

from Smart_lock.python_proccess_communicate.service_finger1 import object_to_array_packet

def thread_readQueue(queue):
    prev_time = 0
    while True:
        if time.time()*1000 - prev_time >= 5000:
            if not queue.empty():
                obj = queue.get()
                print(f"obj_type:{type(obj)}, object value:{obj}")
            else:
                print("can't read queue")
            prev_time = time.time()*1000

def client_process(address, queue):
    thread_queue = threading.Thread(target=thread_readQueue, args=(queue,))
    prev_time = 0
    thread_queue.start()
    
    for i in range(0,4):
        if time.time()*1000 - prev_time >= 5000:
            print(f"Client {1}: Starting client process.")
            conn = Client(address)
            for i in range(3):
                data_object = {
                'client_id':1,
                'request_type': 0x01,
                'request_id': i+1,
                'data_length': 5,
                'data': b'hello'
                }
                bytedata =  object_to_array_packet(data_object)
                print(f"Client {1}: Sending message: {bytedata}")
                conn.send(bytedata)
                response = conn.recv()
                print(f"Client {1}: Received response: {response}")
            conn.send(0xFFFF)
            conn.close()
            print(f"Client {1}: Finished sending messages.")
            prev_time = time.time()
    
    thread_queue.join()
    
