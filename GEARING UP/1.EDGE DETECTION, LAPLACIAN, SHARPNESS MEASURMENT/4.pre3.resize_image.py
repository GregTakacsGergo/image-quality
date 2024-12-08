'''resize_image.py
This script is meant to resize an image to a specified size, in order to provide normalization for image comparison. '''

import os
import cv2
import tkinter as tk
from tkinter import filedialog, Label
from PIL import Image, ImageTk

image_title = ""
output_folder =  "C:\PROGRAMMING\7.image_quality_checker\GEARING UP\1.EDGE DETECTION, LAPLACIAN, SHARPNESS MEASURMENT\resized_images"

def open_and_process_image():
    global image_title
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
    if not image_path:
        print("Error: No image selected.")
        return
    image_title = os.path.splitext(os.path.basename(image_path))[0]
    try:
        # Display the uploaded image in Tkinter
        img = Image.open(image_path)
        #img.thumbnail((250, 250))
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img)
        image_label.image = img

        # Update the window title with the new image title
        root.title(f"Resizing Image - {image_title}")
    
        # Process the image and save it
        process_image(image_path, image_title)
        success_label.config(text=f"Image saved successfully")
    except FileNotFoundError:
        print("Error: Could not find the image file.")

def process_image(image_path, image_title, output_size = (400, 300)):
    output_folder = "resized_images"
    os.makedirs(output_folder, exist_ok=True)

    image = cv2.imread(image_path)
    try: 
        resized_image = cv2.resize(image, output_size, interpolation=cv2.INTER_AREA)
        output_path = os.path.join(output_folder, f"{image_title}_resized_{output_size[0]}x{output_size[1]}.jpg")
        cv2.imwrite(output_path, resized_image)
    except cv2.error:
        print("Error: Could not read the image file.")
        return
    
root = tk.Tk()
root.title("Image Resizer")

button = tk.Button(root, text="Open Image", command=open_and_process_image)
button.pack(pady=20)

image_label = tk.Label(root)
image_label.pack(pady=10)

success_label = Label(root, text="")
success_label.pack(pady=30)
root.mainloop()    