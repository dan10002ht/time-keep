import tkinter as tk
from tkinter import Label, StringVar
from PIL import Image, ImageTk, ImageOps
from datetime import datetime
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
        self.update_frame3_text()  # Start cyclic update for frame3

        # Frame 4: Display fixed and dynamic text
        self.frame4 = tk.Frame(self.root)
        self.frame4.grid(row=2, column=1, rowspan=2, sticky='nsew', pady=10, padx=15)
        for i in range(4):
            self.frame4.grid_rowconfigure(i, weight=1)
        self.frame4.grid_columnconfigure(0, weight=1)

        self.notification_label = Label(self.frame4, text="Notification", justify="left", relief="solid", anchor='nw', bd=0, font=("Helvetica", 20), bg="red")
        self.notification_label.grid(row=0, column=0, rowspan=1, sticky='nsew', pady=5)

        self.dynamic_text_label4 = Label(self.frame4, textvariable=self.dynamic_text_var4, justify="center", anchor='nw', bd=1, relief="solid")
        self.dynamic_text_label4.grid(row=1, column=0, rowspan=3, sticky='nsew', pady=5)
        self.update_frame4_text()

        # Frame 5: Buttons
        self.frame5 = tk.Frame(self.root, bd=1, relief="solid")
        self.frame5.grid(row=4, column=1, sticky='nsew', pady=10, padx=15)
        self.frame5.grid_rowconfigure(0, weight=1)
        self.frame5.grid_columnconfigure(0, weight=1)
        self.frame5.grid_columnconfigure(1, weight=1)

        self.button1 = tk.Button(self.frame5, bg="green", text="Button 1", borderwidth=1, relief="solid", highlightbackground="black", command=self.start_stream)
        self.button1.grid(row=0, column=0, sticky='nsew', pady=20, padx=30)

        self.button2 = tk.Button(self.frame5, bg="red", text="Button 2", borderwidth=1, relief="solid", highlightbackground="black", command=self.stop_stream)
        self.button2.grid(row=0, column=1, sticky='nsew', pady=20, padx=30)

        self.update_dynamic_texts()
        self.display_image()  # Start displaying video

    def display_image(self):
        if self.flag_stream == 1:
            _, frame = self.vid.read()
            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            captured_image = Image.fromarray(opencv_image)
            img = captured_image.resize((512, 512), Image.Resampling.LANCZOS)
            img = ImageOps.fit(img, (512, 512))
            photo_image = ImageTk.PhotoImage(image=img)
            self.label_stream.photo_image = photo_image
            self.label_stream.configure(image=photo_image)
            self.label_stream.after(30, self.display_image)
        else:
            self.label_stream.after(1000, self.display_image)

    def start_stream(self):
        self.flag_stream = 1

    def stop_stream(self):
        self.flag_stream = 0

    def update_time(self):
        current_time = datetime.now().strftime('%A, %H:%M:%S - %d/%m/%Y')
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)

    def update_dynamic_texts(self):
        self.content_var2.set('Dynamic content for frame 3')
        self.content_var3.set('Dynamic content for frame 4')

    def update_frame3_text(self):
        self.content_var2.set(self.cycle_texts[0])
        self.cycle_texts.append(self.cycle_texts.pop(0))  # Rotate the list
        self.root.after(1000, self.update_frame3_text)

    def update_frame4_text(self):
        self.dynamic_text_var4.set('Dynamic content for frame 4')

if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamApp(root)
    root.mainloop()