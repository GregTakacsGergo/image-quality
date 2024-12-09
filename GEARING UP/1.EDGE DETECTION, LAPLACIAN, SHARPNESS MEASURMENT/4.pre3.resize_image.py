'''resize_image.py
This script is meant to resize an image to a specified size, in order to provide normalization for image comparison. '''

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import tkinter as tk
from tkinter import filedialog, Label
from PIL import Image, ImageTk

image_title = ""

def open_and_process_image():
    global image_title
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
    image_title = os.path.splitext(os.path.basename(image_path))[0]
    try:
        # Display the uploaded image in Tkinter
        img = Image.open(image_path)
        #img.thumbnail((250, 250))
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img)
        image_label.image = img

        # Update the window title with the new image title
        root.title(f"Edge Detection Grayscale Image - {image_title}")
    
        # Process the image
        process_image(image_path, image_title)
        success_label.config(text=f"Image saved successfully")
    except FileNotFoundError:
        print("Error: Could not find the image file.")

def process_image(image_path, image_title):
    pass


root = tk.Tk()

button = tk.Button(root, text="Open Image", command=open_and_process_image)
button.pack(pady=20)

image_label = tk.Label(root)
image_label.pack(pady=10)

success_label = Label(root, text="")
success_label.pack(pady=30)
root.mainloop()    