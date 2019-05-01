import tkinter as tk

import cv2
from PIL import ImageTk, Image

LARGE_FONT = ("Verdana", 12)


class CarApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (CameraTest, CarGifPage, NotCarGifPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(CameraTest)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class CameraTest(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        self.button_start = tk.Button(self, text="Start photo_booth", command=self.display_stream)
        self.button_start.grid()

        self.button_snapshot = tk.Button(self, text="snapshot", command=self.stop_stream)

        self.panel = tk.Label(self)

        self.cap = cv2.VideoCapture(0)
        self.video_stream()

    def video_stream(self):
        _, frame = self.cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image).resize((480, 480))
        imgtk = ImageTk.PhotoImage(image=img)
        self.panel.imgtk = imgtk
        self.panel.configure(image=imgtk)
        self.panel.after(1, self.video_stream)

    def display_stream(self):
        self.button_start.grid_forget()
        self.panel.grid()
        self.button_snapshot.grid()

    def stop_stream(self):
        self.panel.grid_forget()
        self.button_snapshot.grid_forget()
        self.button_start.grid()
        self.controller.show_frame(NotCarGifPage)


class CarGifPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        button1 = tk.Button(self, text="Back", command=lambda: controller.show_frame(CameraTest))
        button1.pack(side="bottom", fill="both", expand="yes", padx=10,
                     pady=10)
        self.panel = tk.Label(self)
        self.panel.pack(side="left", padx=10, pady=10)
        self.gif_images = [ImageTk.PhotoImage(image=Image.open(
            '/Users/constant.bridon/Documents/journeeBDA/photobooth_car/car_gif/frame_{}_delay-0.07s.jpg'.format(
                str(x + 1).zfill(2))))
            for x
            in range(48)]
        self.index = 0
        self.animate()

    def animate(self):
        image = self.gif_images[self.index]
        self.panel.configure(image=image)
        self.panel.image = image
        self.index = (self.index + 1) % 48
        self.panel.after(100, self.animate)


class NotCarGifPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        button1 = tk.Button(self, text="Back", command=lambda: controller.show_frame(CameraTest))
        button1.pack(side="bottom", fill="both", expand="yes", padx=10,
                     pady=10)
        self.panel = tk.Label(self)
        self.panel.pack(side="left", padx=10, pady=10)
        self.gif_images = [ImageTk.PhotoImage(image=Image.open(
            '/Users/constant.bridon/Documents/journeeBDA/photobooth_car/not_car_gif/frame_{}_delay-0.03s.jpg'.format(
                str(x + 1).zfill(2))))
            for x
            in range(89)]
        self.index = 0
        self.animate()

    def animate(self):
        image = self.gif_images[self.index]
        self.panel.configure(image=image)
        self.panel.image = image
        self.index = (self.index + 1) % 89
        self.panel.after(100, self.animate)


app = CarApp()
app.mainloop()
