import os
import tkinter as tk

import cv2
import numpy as np
from PIL import ImageTk, Image

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))


class CarApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side='top', fill='both', expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.class_to_display = 0

        self.frames = {}

        for F in (CameraTest, GifPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(CameraTest)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class CameraTest(tk.Frame):
    SHAPE = (640, 480)

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        self.welcome_message = tk.Label(self)
        img = Image.open(os.path.join(PROJECT_PATH, 'welcome_message.jpg')).resize(self.SHAPE)
        img = ImageTk.PhotoImage(image=img)
        self.welcome_message.img = img
        self.welcome_message.configure(image=img)
        self.welcome_message.grid()
        self.button_start = tk.Button(self, text='Start photo booth', command=self.display_stream)
        self.button_start.grid()

        self.button_snapshot = tk.Button(self, text='snapshot', command=self.make_inference)
        self.panel = tk.Label(self)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

        self.video_stream()

    def video_stream(self):
        _, frame = self.cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.panel.imgtk = imgtk
        self.panel.configure(image=imgtk)
        self.panel.after(1, self.video_stream)

    def display_stream(self):
        self.button_start.grid_forget()
        self.welcome_message.grid_forget()
        self.panel.grid()
        self.button_snapshot.grid()

    def make_inference(self):
        self.panel.grid_forget()
        self.button_snapshot.grid_forget()
        self.welcome_message.grid()
        self.button_start.grid()
        self.controller.class_to_display = np.random.randint(0, 2)
        self.controller.frames[GifPage].index = 0
        self.controller.show_frame(GifPage)


class GifPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.panel = tk.Label(self)
        self.panel.grid(ipadx=80)

        self.controller = controller
        button_back = tk.Button(self, text='Back', command=lambda: self.controller.show_frame(CameraTest))
        button_back.grid()

        self.gif_images = {
            0: [ImageTk.PhotoImage(image=Image.open(os.path.join(PROJECT_PATH, 'car_gif', f'frame_{str(x + 1).zfill(2)}_delay-0.07s.jpg'))) for x in range(48)],
            1: [ImageTk.PhotoImage(image=Image.open(os.path.join(PROJECT_PATH, 'not_car_gif', f'frame_{str(x + 1).zfill(2)}_delay-0.03s.jpg'))) for x in range(89)]
        }
        self.index = 0

        self.animate()

    def animate(self):
        image = self.gif_images[self.controller.class_to_display][self.index]
        self.panel.configure(image=image)
        self.panel.image = image
        self.index = (self.index + 1) % len(self.gif_images[self.controller.class_to_display])
        self.panel.after(100, self.animate)


app = CarApp()
app.mainloop()