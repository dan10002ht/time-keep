import tkinter as tk
from tkinter import Label, StringVar
from PIL import Image, ImageTk, ImageOps
from datetime import datetime
from threading import Thread
import cv2


class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1024x600")
        self.root.title("Webcam App")

        self.cam_width, self.cam_height = 512, 512
        self.vid = cv2.VideoCapture(0)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
        self.flag_stream = 1
        self.last_flag_stream = 0
        self.flag_submit = 0
        self.flag_genFaceID = 0
        self.finger_id = None
        self.face_id = None
        self.cycle_texts = ['Text 1', 'Text 2', 'Text 3', 'Text 4']

        for i in range(5):
            self.root.grid_rowconfigure(i, weight=1)
        for j in range(2):
            self.root.grid_columnconfigure(j, weight=1)

        self.id_var = StringVar()
        self.content_var2 = StringVar()
        self.content_var3 = StringVar()
        self.time_var = StringVar()
        self.dynamic_text_var4 = StringVar()

        self.setup_gui()
    def register_callback_submit(self, calback_submit = None):
        self.cbk_submit  = calback_submit
    def register_callback_genFaceID(self, callback_thread_genFaceID = None):
        self.cbk_genFaceID  = callback_thread_genFaceID
    def setup_gui(self):
        # Frame 1: Display Image
        self.frame1 = tk.Frame(self.root, bd=0, relief="solid")
        self.frame1.grid(row=0, column=0, rowspan=5, sticky='nsew', pady=(30,40), padx=10)
        self.label_stream = Label(self.frame1, bg='lightblue')
        self.label_stream.pack(expand=True)

        # Frame 2: Display fixed and dynamic text
        self.frame2 = tk.Frame(self.root, bd=1, relief="solid")
        self.frame2.grid(row=0, column=1, sticky='nsew', pady=10, padx=15)
        self.time_label = Label(self.frame2, textvariable=self.time_var, font=("Helvetica", 20), justify="left")
        self.time_label.pack(fill="both", expand=True)
        self.update_time()  # Start updating time

        # Frame 3: Display fixed and dynamic text
        self.frame3 = tk.Frame(self.root, bd=1, relief="solid")
        self.frame3.grid(row=1, column=1, sticky='nsew', pady=10, padx=15)
        self.frame3_text = Label(self.frame3, textvariable=self.content_var2, font=("Helvetica", 20), justify="left")
        self.frame3_text.pack(fill="both", expand=True)

        # Frame 4: Display fixed and dynamic text
        self.frame4 = tk.Frame(self.root)
        self.frame4.grid(row=2, column=1, rowspan=2, sticky='nsew', pady=10, padx=15)
        for i in range(4):
            self.frame4.grid_rowconfigure(i, weight=1)
        self.frame4.grid_columnconfigure(0, weight=1)

        self.notification_label = Label(self.frame4, text="Notification", justify="center", relief="solid", bd=0, font=("Helvetica", 20), bg="yellow", fg = "red")
        self.notification_label.grid(row=0, column=0, rowspan=1, sticky='nsew', pady=5)

        self.dynamic_text_label4 = Label(self.frame4, textvariable=self.dynamic_text_var4, justify="center", anchor='nw', bd=1, relief="solid")
        self.dynamic_text_label4.grid(row=1, column=0, rowspan=3, sticky='nsew', pady=5)

        # Frame 5: Buttons
        self.frame5 = tk.Frame(self.root, bd=1, relief="solid")
        self.frame5.grid(row=4, column=1, sticky='nsew', pady=10, padx=15)
        self.frame5.grid_rowconfigure(0, weight=1)
        self.frame5.grid_columnconfigure(0, weight=1)
        self.frame5.grid_columnconfigure(1, weight=1)
        self.frame5.grid_columnconfigure(2, weight=1)

        self.button1 = tk.Button(self.frame5, bg="#0de0cf", text="CHECKIN", borderwidth=1, relief="solid", highlightbackground="black", command=self.submit_callback)
        self.button1.grid(row=0, column=0, sticky='nsew', pady=20, padx=30)

        self.button2 = tk.Button(self.frame5, bg="#fdebb9", text="GET FACEID", borderwidth=1, relief="solid", highlightbackground="black", command=self.Face_ID_callback)
        self.button2.grid(row=0, column=1, sticky='nsew', pady=20, padx=30)

        self.button2 = tk.Button(self.frame5, bg="pink", text="CHECK OUT", borderwidth=1, relief="solid", highlightbackground="black", command=self.submit_callback_checkout)
        self.button2.grid(row=0, column=2, sticky='nsew', pady=20, padx=30)

        self.display_image()  # Start displaying video
        self.update_ID_Content()
        #  call proccess 

    def display_image(self):
        if self.flag_stream == 1:
            _, frame = self.vid.read()
            self.frame_recog = frame
            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            self.captured_image = Image.fromarray(opencv_image)
            img = self.captured_image.resize((512, 512), Image.Resampling.LANCZOS)
            img = ImageOps.fit(img, (512, 512))
            photo_image = ImageTk.PhotoImage(image=img)
            self.label_stream.photo_image = photo_image
            self.label_stream.configure(image=photo_image)
            self.label_stream.after(20, self.display_image)
        else:
            self.label_stream.after(1000, self.display_image)

    def register_Check_ID_Callback(self, checkID_Callback = None):
        self.cbk_CheckID = checkID_Callback

    def register_buzzer_error(self, callback_buzzer = None):
        self.callback_buzzer = callback_buzzer
    def submit_callback(self):
        print("Submit callback")
        if(self.face_id != None and self.finger_id != None):
            self.flag_submit = 1
            content = ""
            self.update_Notification(content=content, type_notify= 2)
        else:
            finger_id_content ="Finger ID not found" if self.finger_id is None else ""
            face_id_content = ( "\n Face ID not found" if self.face_id is None else "")
            content = finger_id_content + face_id_content
            self.update_Notification(content=content, type_notify= 2)
            self.callback_buzzer()

        if self.cbk_submit != None and self.flag_submit == 1:
            self.flag_stream = 1
            self.flag_submit = 0
            ID = {"finger_id":self.finger_id, "face_id":self.face_id}
            resp = self.cbk_submit(self.timestamp, ID)
            if resp:
                content  = "checkin successs!"
                self.update_Notification(content=content, type_notify= 0)
            else:
                content  = "checkin Fail, retry!"
                self.update_Notification(content=content, type_notify= 0)
            
            self.finger_id = None
            self.face_id = None
            print(resp)

    def submit_callback_checkout(self):
        print("Submit Checkout callback")
        if(self.face_id != None and self.finger_id != None):
            self.flag_submit = 1
        else:
            finger_id_content ="Finger ID not found" if self.finger_id is None else ""
            face_id_content = ( "\n Face ID not found" if self.face_id is None else "")
            content = finger_id_content + face_id_content
            self.update_Notification(content=content, type_notify= 2)

        if self.cbk_submit != None and self.flag_submit == 1:
            self.flag_stream = 1
            self.flag_submit = 0
            resp = self.cbk_submit(self.timestamp, self.finger_id)
            if resp:
                content  = "checkout successs!"
                self.update_Notification(content=content, type_notify= 0)
            else:
                content  = "checkout Fail, retry!"
                self.update_Notification(content=content, type_notify= 0)
            
            self.finger_id = None
            self.face_id = None
            print(resp)
    
    def Face_ID_callback(self):
        if(self.cbk_genFaceID != None and self.flag_genFaceID == 0):
            self.flag_stream = 0
            self.cbk_genFaceID(self.frame_recog)
            self.flag_genFaceID = 1
        

    def update_time(self):
        self.timestamp = datetime.now()
        current_time = self.timestamp.strftime('%A, %H:%M:%S - %d/%m/%Y')
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)

    def update_dynamic_texts(self):
        self.content_var2.set('Dynamic content for frame 3')
        self.content_var3.set('Dynamic content for frame 4')

    def update_ID_Content(self):
        finger_id_content = "Finger ID:" + (str(self.finger_id) if self.finger_id is not None else "N/A")
        face_id_content = "\nFace ID:" +( str(self.face_id) if self.face_id is not None else "N/A")
        content = finger_id_content + face_id_content
        self.content_var2.set(content)

        self.root.after(1000, self.update_ID_Content)

    def update_Notification(self, content:str = "", type_notify  = 0):
        print(content)
        self.update_frame4_text(content)
        match type_notify:
            case 0: 
                self.dynamic_text_label4.configure(fg="green")
            case 1: 
                self.dynamic_text_label4.configure(fg="yellow")
            case 2: 
                self.dynamic_text_label4.configure(fg="red")

    def update_frame4_text(self, content):
        self.dynamic_text_var4.set(content)
    
    def update_finger_sensor(self, object = None):
        if object != None:
            print(f"=>>>> object to display:{object}")
            if object["Result"]["status"] != 1:
                self.update_Notification("Finger sensor error!!", 2)
            else:
                self.finger_id = object["Result"]["Data"]["ID"]
        print("=======> Finger ID = ",self.finger_id)
    def update_face_id(self, face_object):
        print(face_object["Result"]["ID"])
        if face_object["Result"]["ID"]:
            self.face_id = face_object["Result"]["ID"]
        print("=======> Face ID = ",self.finger_id)
        self.flag_stream = 1
        self.flag_genFaceID = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamApp(root)
    root.mainloop()
