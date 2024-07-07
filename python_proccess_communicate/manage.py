# main.py
import multiprocessing
import multiprocessing.queues
import time
import server
import client

def start_server(address, queue):
    server_proc = multiprocessing.Process(target=server.server_process, args=(address,queue,))
    server_proc.start()
    return server_proc

def start_client(address, queue):
    client_proc = multiprocessing.Process(target=client.client_process, args=(address, queue,))
    client_proc.start()
    return client_proc

if __name__ == "__main__":
    address = ('localhost', 6000)
    
    #start a queue
    queue_finger = multiprocessing.Queue()

    # Start the server process
    server_proc = start_server(address, queue_finger)

    # Start multiple client processes
    
    client_proc = start_client(address, queue_finger)
    client_proc.join()

    # # Stop the server
    server_proc.terminate()
    server_proc.join()
    print("Main: All processes have been terminated.")