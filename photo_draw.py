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
        self.text = tk.Label(self,
                             text="Welcome to the car drawing detector !"
                                  "\n Click on the button below "
                                  "\n and draw something",
                             bd=1, font='{Comic Sans MS} 16')
        self.text.grid(padx=30, pady=80)

        self.button_start = tk.Button(self, text='20 seconds to draw', command=self.display_canvas)
        self.button_start.grid(padx=30)

        self.canvas = tk.Canvas(self, width=460, height=300)
        self.image = Image.new("RGB", (460, 300), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
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
            self.canvas.create_line(x, y, x1, y1, width=10)
            self.draw.line([x, y, x1, y1], (0, 0, 0), 5)
        self.canvas.old_coords = x, y
        self.canvas.event_time = event_time

    def make_inference(self):
        self.canvas.delete("all")
        self.canvas.grid_forget()
        self.label.grid_forget()
        image = self.image.resize((128, 128)).convert('L')

        self.image = Image.new("RGB", (460, 300), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

        self.text.grid(padx=30, pady=80)
        self.button_start.grid(padx=30)

        image.save(os.path.join(PROJECT_PATH, 'last_capture.jpg'))
        image = np.array(image.convert('RGB')).reshape((1, 128, 128, 3))

        ### https://www.codeastar.com/visualize-convolutional-neural-network/

        import matplotlib.pyplot as plt
        plt.imshow(image[0])
        from keras.models import Model
        layer_outputs = [layer.output for layer in self.model.layers]
        activation_model = Model(inputs=self.model.input, outputs=layer_outputs)
        activations = activation_model.predict(image)

        def display_activation(activations, col_size, row_size, act_index):
            activation = activations[act_index]
            activation_index = 0
            fig, ax = plt.subplots(row_size, col_size, figsize=(row_size * 2.5, col_size * 1.5))
            for row in range(0, row_size):
                for col in range(0, col_size):
                    ax[row][col].imshow(activation[0, :, :, activation_index], cmap='gray')
                    activation_index += 1

        print(self.model.summary())

        ### see filter
        weight_conv2d_1 = self.model.layers[0].get_weights()[0][:, :, 0, :]

        col_size = 8
        row_size = 4
        filter_index = 0
        fig, ax = plt.subplots(row_size, col_size, figsize=(12, 8))
        for row in range(0, row_size):
            for col in range(0, col_size):
                ax[row][col].imshow(weight_conv2d_1[:, :, filter_index], cmap="gray")
                filter_index += 1

        ### see activation map layer 0 (32 features, 3x3 conv)
        display_activation(activations, 8, 4, 0)
        plt.show()

        ### see activation map layer 1 (max pull)
        display_activation(activations, 8, 4, 1)
        plt.show()

        ### see activation map layer 3 (20 feat, 3x3 + max pull)
        display_activation(activations, 5, 4, 3)
        plt.show()

        ### see activation map layer 5 (12 feat, 3x3 + max pull)
        display_activation(activations, 4, 3, 5)
        plt.show()

        ### see activation map layer 7 (8 feat, 3x3 + max pull)
        display_activation(activations, 4, 2, 7)
        plt.show()


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
