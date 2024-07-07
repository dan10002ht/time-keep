# server.py
import multiprocessing
from multiprocessing.connection import Listener
import  Smart_lock.python_proccess_communicate.service_finger1 as service_finger1 
import time
import threading 
import json

Finger = service_finger1.finger()
# Đọc file JSON

def handle_service_finger(queue:multiprocessing.queues.Queue,service_type, request_id,data_packet = None):
    resp = []
    match service_type:
        case service_finger1._SERVICE_REQUEST_fINGER:
            print("Request finger scan")
            # TODO: Function process read finger, that return object information and status
            res_finger = Finger.Service_ScanFinger()
            # TODO: Enqueue
            obj = {"ID":1, "service_id":request_id,"accept":True,"role":1}
            
            if res_finger["status"] == True:
            #return success
                
                res_enqueue = Enqueue(queue,obj)
                if(res_enqueue != True):
                    resp = [0xFF]
                else:
                    resp = [0x01]
    
            elif res_finger["status"] == False:
                resp = [0xFF]
        case service_finger1._SERVICE_FINGER_TYPE_ENROLL:
            print("Request Enroll")
            return "Two"
        case 3:
            return "Three"
        case _:
            return "Default case"
    return resp
#  This thread read fingerprint cyclic 5000ms and enqueue
def Enqueue(queue:multiprocessing.queues.Queue, obj_queue):
    obj = {"ID":obj_queue["ID"],"ts": time.time()*1000, "service_request":obj_queue["service_id"],"accept":obj_queue["accept"],"role":obj_queue["role"]}
    try:
        queue.put(obj)
        print("----- queue put sucess!!")
        return True
    except:
        print("-------- queue put fail!!")
        return False

    
def handle_service_job(data_packet, conn, queue:multiprocessing.queues.Queue):
    try:
        print(data_packet)
        obj_request = service_finger1.Parse_Request(data_packet)
    except:
        print("Parse fail")
        obj_request = None
    print("Data object")
    print(obj_request)
    if(obj_request != None):
        resp_data = handle_service_finger(queue,obj_request["request_type"],obj_request["request_id"],obj_request["data"])
        print("response data:",resp_data)
        response = [0xFE,0xEE,resp_data]
    else:
        response = [0xFE, 0xEE, 0xFF]
    conn.send(response)

def handle_client(conn, queue:multiprocessing.queues.Queue):
    while True:
        try:
            message = conn.recv()
            print(message)
            if message == 0xFFFF:
                print("Server: Stopping client handler.")
                break
            handle_service_job(message, conn, queue)
            
        except EOFError:
            break
    conn.close()

# This thread process service with client 
def thread_server(queue:multiprocessing.queues.Queue, address,):
    print("Server: Starting server process.")
    listener = Listener(address)

    while True:
        conn = listener.accept()
        if conn:
            client_process = threading.Thread(target=handle_client, args=(conn,queue,))
            client_process.start()

def quey_datasheet(datasheet, obj_id):
    obj_query = None
    obj_query = [item for item in datasheet if item['accept']]
    return obj_query

def server_process(address, queue, ):
    try:
        with open('data.json', 'r') as file:
            dataset = json.load(file)
    except:
        dataset = None
    block_event = threading.Event()
    block_event.set()
    thread_serverhandle  = threading.Thread(target=thread_server, args=(queue,address,))

    # Start the threads
    thread_serverhandle.start()

    # Wait for the threads to finish (they won't in this infinite loop example)
    thread_serverhandle.join()