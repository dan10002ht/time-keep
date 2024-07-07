import requests
import base64
import cv2
# Function to encode image to base64
def encode_image_to_base64(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    encoded_string = base64.b64encode(buffer)
    decode =  encoded_string.decode()
    return "data:image/jpeg;base64,"+ str(decode)


class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None

    def login(self, endpoint, username, password):
        url = f"{self.base_url}/login"
        data = {
            'username': username,
            'password': password
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            self.token = response.json().get('token')
            print("Login successful, token stored.")
        else:
            print("Login failed:", response.text)
    
    def post(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': self.token,
        }
        response = requests.post(url, json=data, headers=headers)
        print(response.text)
        return response

    def reuquest_checkin(self, image, ID):
        endpoint = f"time/{ID}"
        self.image_frame = encode_image_to_base64(image)
        print(self.image_frame[0:100])
        data = {"image":self.image_frame}
        ret = self.post(endpoint=endpoint, data = data)
        print(ret.text)
        self.image_frame = ""
        return ret
