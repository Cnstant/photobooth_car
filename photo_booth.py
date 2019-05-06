import os
import tkinter as tk

import cv2
import numpy as np
from PIL import ImageTk, Image
from keras.models import load_model

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

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        self.text = tk.Label(self,
                             text="Welcome to the car drawing Photo Booth !"
                                  "\n To infer if your drawing is a car"
                                  "\n click on start photo booth then snapshot ",
                             bd=1, font='{Comic Sans MS} 16')
        self.text.grid(padx=30, pady=80)
        self.button_start = tk.Button(self, text='Start photo booth', command=self.display_stream)
        self.button_start.grid(padx=30)

        self.button_snapshot = tk.Button(self, text='snapshot', command=self.make_inference)
        self.panel = tk.Label(self)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 160)
        self.cap.set(4, 120)

        self.video_stream()

        self.model = load_model(os.path.join(PROJECT_PATH, 'model.h5'))
        self.img = None

    def video_stream(self):
        _, frame = self.cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        self.img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=self.img)
        self.panel.imgtk = imgtk
        self.panel.configure(image=imgtk)
        self.panel.after(1, self.video_stream)

    def display_stream(self):
        self.button_start.grid_forget()
        self.text.grid_forget()
        self.panel.grid(padx=30)
        self.button_snapshot.grid()

    def make_inference(self):
        self.panel.grid_forget()
        self.button_snapshot.grid_forget()
        self.text.grid(padx=30, pady=80)
        self.button_start.grid(padx=30)

        image = self.img.resize((128, 128), Image.ANTIALIAS).convert('L')
        image = np.array(image)
        image[image < 100] = 0
        image[image > 100] = 255
        image = Image.fromarray(image).convert('RGB')
        image.save(os.path.join(PROJECT_PATH, 'last_capture.jpg'))
        image = np.array(image).reshape((1, 128, 128, 3))

        prediction = self.model.predict_classes(image)[0][0]
        self.controller.class_to_display = prediction
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
            0: [ImageTk.PhotoImage(
                image=Image.open(
                    os.path.join(PROJECT_PATH, 'car_gif', 'frame_{}.jpg'.format(str(x + 1).zfill(2)))).resize(
                    (200, 240))) for x in
                range(48)],

            1: [ImageTk.PhotoImage(
                image=Image.open(
                    os.path.join(PROJECT_PATH, 'not_car_gif', 'frame_{}.jpg'.format(str(x + 1).zfill(2)))).resize(
                    (200, 240))) for x
                in range(89)]

        }
        self.index = 0

        self.animate()

    def animate(self):
        image = self.gif_images[self.controller.class_to_display][self.index]
        self.panel.configure(image=image)
        self.panel.image = image
        self.index = (self.index + 1) % len(self.gif_images[self.controller.class_to_display])
        self.panel.after(100, self.animate)


if __name__ == '__main__':
    app = CarApp()
    app.mainloop()
