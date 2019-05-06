import io
import os
import tkinter as tk

import numpy as np
from PIL import Image, ImageTk
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

        for F in (DrawTest, GifPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(DrawTest)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class DrawTest(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        self.text = tk.Label(self,
                             text="Welcome to the car drawing detector !"
                                  "\n Click on the button below "
                                  "\n and draw something",
                             bd=1, font='{Comic Sans MS} 16')
        self.text.grid(padx=30, pady=80)

        self.button_start = tk.Button(self, text='20 seconds to draw', command=self.display_canvas)
        self.button_start.grid(padx=30)

        self.canvas = tk.Canvas(self, width=160, height=120)
        self.canvas.old_coords = None
        self.canvas.event_time = None

        self.counter = 20

        self.label = tk.Label(self, fg="green")
        self.label.config(text=self.counter)

        self.model = load_model(os.path.join(PROJECT_PATH, 'model.h5'))

    def display_canvas(self):
        self.button_start.grid_forget()
        self.text.grid_forget()
        self.canvas.grid(padx=10, pady=10)
        self.label.grid()
        self.controller.bind('<B1-Motion>', self.drawing)
        self.counter_label(self.label)

    def counter_label(self, label):
        def count():
            self.counter -= 1
            if self.counter != 0:
                self.label.config(text=self.counter)
                self.label.after(1000, count)
            else:
                self.counter = 20
                self.make_inference()

        count()

    def drawing(self, event):

        x, y = event.x, event.y
        event_time = event.time
        if self.canvas.old_coords and (event_time - self.canvas.event_time) < 200:
            x1, y1 = self.canvas.old_coords
            self.canvas.create_line(x, y, x1, y1, width=1)
        self.canvas.old_coords = x, y
        self.canvas.event_time = event_time

    def make_inference(self):

        ps = self.canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))

        self.canvas.delete("all")
        self.canvas.grid_forget()
        self.label.grid_forget()
        self.text.grid(padx=30, pady=80)
        self.button_start.grid(padx=30)

        img = img.resize((128, 128))
        img.save(os.path.join(PROJECT_PATH, 'last_capture.jpg'))
        image = np.array(img).reshape((1, 128, 128, 3))

        prediction = self.model.predict_classes(image)[0][0]
        self.controller.class_to_display = prediction
        self.controller.frames[GifPage].index = 0
        self.controller.show_frame(GifPage)


class GifPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.panel = tk.Label(self)
        self.panel.grid(padx=80)

        self.controller = controller
        button_back = tk.Button(self, text='Back', command=lambda: self.controller.show_frame(DrawTest))
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
