import tkinter as tk

import numpy as np

root = tk.Tk()


def myfunction(event):
    x, y = event.x, event.y
    if canvas.old_coords and np.sqrt((x - canvas.old_coords[0]) ** 2 + (y - canvas.old_coords[1]) ** 2) <= 20:
        x1, y1 = canvas.old_coords
        canvas.create_line(x, y, x1, y1)
    canvas.old_coords = x, y


def display_canvas():
    button.grid_forget()
    canvas.grid(padx=10, pady=10)
    label.grid()
    root.bind('<B1-Motion>', myfunction)
    counter_label(label)


counter = 20


def counter_label(label):
    def count():
        global counter
        counter -= 1
        if counter != 0:
            label.config(text=counter)
            label.after(1000, count)
        else:
            counter = 20
            make_inference_on_frame()

    count()


label = tk.Label(root, fg="green")
label.config(text=counter)

canvas = tk.Canvas(root, width=460, height=300)

canvas.old_coords = None

button = tk.Button(root, text='20 seconds to draw !', command=display_canvas)
button.grid()

root.mainloop()
