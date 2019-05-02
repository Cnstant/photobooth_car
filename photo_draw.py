import os
import tkinter as tk

import numpy as np
from PIL import Image, ImageDraw, ImageTk
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
        self.welcome_message = tk.Label(self)
        img = Image.open(os.path.join(PROJECT_PATH, 'welcome_message.jpg')).resize((320, 240))
        img = ImageTk.PhotoImage(image=img)
        self.welcome_message.img = img
        self.welcome_message.configure(image=img)
        self.welcome_message.grid(padx=30)
        self.button_start = tk.Button(self, text='20 seconds to draw', command=self.display_canvas)
        self.button_start.grid(padx=30)

        self.canvas = tk.Canvas(self, width=460, height=300)
        self.image = Image.new("RGB", (460, 300), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        self.canvas.old_coords = None

        self.counter = 20

        self.label = tk.Label(self, fg="green")
        self.label.config(text=self.counter)

        self.model = load_model(os.path.join(PROJECT_PATH, 'model.h5'))

    def display_canvas(self):
        self.button_start.grid_forget()
        self.welcome_message.grid_forget()
        self.canvas.grid(padx=10, pady=10)
        self.label.grid()
        self.controller.bind('<B1-Motion>', self._myfunction)
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

    def _myfunction(self, event):
        x, y = event.x, event.y
        if self.canvas.old_coords and np.sqrt(
                (x - self.canvas.old_coords[0]) ** 2 + (y - self.canvas.old_coords[1]) ** 2) <= 20:
            x1, y1 = self.canvas.old_coords
            self.canvas.create_line(x, y, x1, y1)
            self.draw.line([x, y, x1, y1], (0, 0, 0), 5)
        self.canvas.old_coords = x, y

    def make_inference(self):
        self.canvas.delete("all")
        self.canvas.grid_forget()
        self.label.grid_forget()
        image = self.image.resize((128, 128)).convert('L')

        self.image = Image.new("RGB", (460, 300), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

        self.welcome_message.grid(padx=30)
        self.button_start.grid(padx=30)

        image.save(os.path.join(PROJECT_PATH, 'last_capture.jpg'))
        image = np.array(image.convert('RGB')).reshape((1, 128, 128, 3))

        prediction = self.model.predict_classes(image)[0][0]
        print(prediction)
        self.controller.class_to_display = prediction
        self.controller.frames[GifPage].index = 0
        self.controller.show_frame(GifPage)


class GifPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.panel = tk.Label(self)
        self.panel.grid(ipadx=80)

        self.controller = controller
        button_back = tk.Button(self, text='Back', command=lambda: self.controller.show_frame(DrawTest))
        button_back.grid()

        self.gif_images = {
            0: [ImageTk.PhotoImage(
                image=Image.open(os.path.join(PROJECT_PATH, 'car_gif', f'frame_{str(x + 1).zfill(2)}.jpg')).resize(
                    (200, 240))) for x in
                range(48)],

            1: [ImageTk.PhotoImage(
                image=Image.open(os.path.join(PROJECT_PATH, 'not_car_gif', f'frame_{str(x + 1).zfill(2)}.jpg')).resize(
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
