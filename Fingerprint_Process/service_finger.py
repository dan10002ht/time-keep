# Packet request service:
#  1 byte -> Service start 0xFF // 1 byte - Service ID // 1 byte - Service Type // 1 byte -> Service data length // data // END 0xEE
_SERVICE_START = 0XFF
_SERVICE_END   = 0XEE

_SERVICE_REQUEST_fINGER = 0x01
_SERVICE_FINGER_TYPE_FIND = 0X02
_SERVICE_FINGER_TYPE_ENROLL = 0X03 # enroll with ID 1 - 256
_SERVICE_FINGER_TYPE_EREASE_ID = 0X04
_SERVICE_FINGER_TYPE_DOWNLOAD_IMAGE = 0X05
_SERVICE_FINGER_TYPE_SOFT_RESET = 0X06

_SERVICE_FINGER_TYPE_CHECK_MODULE = 0X00 # ping alive

_SERVICE_RESPONSE_PENDING        = 0xFE

import hashlib
import tempfile
from pyfingerprint.pyfingerprint import PyFingerprint
from pyfingerprint.pyfingerprint import FINGERPRINT_CHARBUFFER1
import time 
import json
import os

def Parse_Request(bytedata):
    # Check for the start and end markers
    if not bytedata.startswith(b'\xFF\xEE') or not bytedata.endswith(b'\xEE\xEE'):
        raise ValueError("Invalid data: Missing start or end markers")

    # Remove the start and end markers
    bytedata = bytedata[2:-2]

    # Parse the ClientID (4 bytes, big-endian)
    client_id = int.from_bytes(bytedata[:4], byteorder='big')

    # Parse the request type (1 byte)
    request_type = bytedata[4]

    # Parse the request id (2 bytes, big-endian)
    request_id = int.from_bytes(bytedata[5:7], byteorder='big')

    # Parse the data length (1 byte)
    data_length = bytedata[7]

    # Extract the data (data_length bytes)
    data = bytedata[8:8+data_length]

    # Verify the actual length matches the expected data length
    if len(data) != data_length:
        raise ValueError("Invalid data: Data length mismatch")

    return {
        'client_id': client_id,
        'request_type': request_type,
        'request_id': request_id,
        'data_length': data_length,
        'data': data
    }

def object_to_array_packet(obj):
    # Start marker
    start_marker = b'\xFF\xEE'
    
    # ClientID (4 bytes, big-endian)
    client_id = obj['client_id'].to_bytes(4, byteorder='big')
    
    # Request type (1 byte)
    request_type = obj['request_type'].to_bytes(1, byteorder='big')
    
    # Request ID (2 bytes, big-endian)
    request_id = obj['request_id'].to_bytes(2, byteorder='big')
    
    # Data length (1 byte)
    data_length = obj['data_length'].to_bytes(1, byteorder='big')
    
    # Data
    data = obj['data']
    
    # End marker
    end_marker = b'\xEE\xEE'
    
    # Combine all parts into the final packet
    packet = start_marker + client_id + request_type + request_id + data_length + data + end_marker
    return packet

class finger:
    def __init__ (self, port = "/dev/ttyS0"):
        self.port = port
        self.Flag_init = False
        try:
            self.f = PyFingerprint(port = "/dev/ttyS0", baudRate=57600, address = 0xFFFFFFFF, password = 0x00000000)
            if ( self.f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')
            else:
                print("Init Done")
                self.Flag_init = True
        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            exit(1)

    def Service_ScanFinger(self):
        res = {"status":0, 'Data':{"ID": -1, "accept": False, "role": -1}}
        if(self.Flag_init == True):
            ## Gets some sensor information
            print('Currently used templates: ' + str(self.f.getTemplateCount()) +'/'+ str(self.f.getStorageCapacity()))
            ## Tries to search the finger and calculate hash
            try:
                print('Waiting for finger...')

                ## Wait that finger is read
                while ( self.f.readImage() == False ):
                    print('Finger is being read')
                    pass
                ## Converts read image to characteristics and stores it in charbuffer 1
                self.f.convertImage(FINGERPRINT_CHARBUFFER1)
                ## Searchs template
                result = self.f.searchTemplate()
                positionNumber = result[0]
                accuracyScore = result[1]
                if ( positionNumber == -1 ):
                    print('No match found!')
                else:
                    print('Found template at position #' + str(positionNumber))
                    print('The accuracy score is: ' + str(accuracyScore))
                    res['status'] = 1
                    res_scan = self.get_object_byID(positionNumber)
                    res["Data"]['ID'] = res_scan['ID']
                    res["Data"]['accept'] = res_scan['accept']
                    res["Data"]['role'] = res_scan['role']
                    
                    print(f"Object return {res}")
                ## OPTIONAL stuff
                ## Loads the found template to charbuffer 1
                self.f.loadTemplate(positionNumber, FINGERPRINT_CHARBUFFER1)

                ## Downloads the characteristics of template loaded in charbuffer 1
                characterics = str(self.f.downloadCharacteristics(FINGERPRINT_CHARBUFFER1)).encode('utf-8')

                ## Hashes characteristics of template
                print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())

            except Exception as e:
                print('Operation failed!')
                print('Exception message: ' + str(e))
        else:
            print("Not init sensor")
        return res
    
    def Service_Download_Image(self, file_destination):
        res = 0
        print("Service download image!!")
         ## Wait that finger is read
        if(self.Flag_init == True):
            print('Currently used templates: ' + str(self.f.getTemplateCount()) +'/'+ str(self.f.getStorageCapacity()))

            ## Tries to read image and download it
            try:
                print('Waiting for finger...')

                ## Wait that finger is read
                while ( self.f.readImage() == False ):
                    pass

                print('Downloading image (this take a while)...')

                self.f.downloadImage(file_destination)

                print('The image was saved to "' + file_destination + '".')

            except Exception as e:
                print('Operation failed!')
                print('Exception message: ' + str(e))


        else:
            print("Not init sensor")
        return res
    
    def Service_Enroll(self):
        res = {"status": 1, "ID": -1}
        if(self.Flag_init == True):
            # res_scan = self.Service_ScanFinger()
            # positionNumber = res_scan["ID"]
            # print(f"ID_FOUND = {positionNumber}")
            # if ( positionNumber >= 0 ):
            #     print('Template already exists at position #' + str(positionNumber))
            #     res["status"] = 2
            #     exit(0)
            time.sleep(2)

            print('Waiting for same finger again...')

            ## Wait that finger is read again
            current_time = time.time() *1000
            while ( (self.f.readImage() == False)):
                if time.time()*1000 - current_time >= 5000:
                    break
                pass
            if(time.time()*1000 - current_time >= 5000):
                print("timeout occur!!!")
            else:
                ## Converts read image to characteristics and stores it in charbuffer 2
                self.f.convertImage(0x02)

                ## Compares the charbuffers
                if ( self.f.compareCharacteristics() != 0 ):
                    res["status"] = 3
                    raise Exception('Fingers match')

                ## Creates a template
                self.f.createTemplate()

                ## Saves template at new position number
                positionNumber = self.f.storeTemplate()
                print('Finger enrolled successfully!')
                print('New template position #' + str(positionNumber))
                res["status"] = 0
                res["ID"] = positionNumber
        else:
            print("Not init sensor")

        return res

    def Service_Delete(self, ID):
        res = 1
        if(self.Flag_init == True):
            if ( self.f.deleteTemplate(ID) == True ):
                print('Template deleted!')
                res = 0
        return res
    
    def get_object_byID(self, ID):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(current_dir, 'dataset.json')
        print("file json path:",file_path)
        print(f"ID to check dataset{ID}")
        res = {"ID": ID, "accept": False, "role": -1}
        if(ID >= 0):
            with open(file_path, 'r') as file:
                data = json.load(file)
        
            obj = [item for item in data if(item['ID'] == ID)]
            print(obj)
            res['accept'] = obj[0]['accept']
            res['role'] = obj[0]['role']
        print(f"----------- response: {res}")
        return res

f = finger()

f.Service_ScanFinger()


