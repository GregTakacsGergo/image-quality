'''resize_image.py
This script is meant to resize an image to a specified size, in order to provide normalization for the later image comparison. 
You can open an image - see the original size - and then resize it to a desired size. The resized image will be saved in a new relative folder.
'''

import os
import cv2
import tkinter as tk
from tkinter import simpledialog, filedialog, Label
from PIL import Image, ImageTk

image_title = ""
output_folder =  ""

def open_and_process_image():
    global image_title
    # Open file dialog to select the image
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
    if not image_path:
        print("Error: No image selected.")
        return
    # Extract image title for saving purposes
    image_title = os.path.splitext(os.path.basename(image_path))[0]
    try:
        # Display the uploaded image in Tkinter
        img = Image.open(image_path)
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img)
        image_label.image = img
        # Update the window title with the new image title
        root.title(f"Resizing original Image - {image_title}")
        # Process the image and save it
        process_image(image_path, image_title)
        success_label.config(text=f"Image saved successfully")
        print(f"Saved resized image as '{output_folder}/{image_title}_resized.jpg'")
    except FileNotFoundError:
        print("Error: Could not find the image file.")

def process_image(image_path, image_title, output_size = (400, 300)):
    output_folder = "GEARING UP/SEASON1. EDGE DETECTION, LAPLACIAN, SHARPNESS MEASURMENT/resized_images/"
    os.makedirs(output_folder, exist_ok=True)
    image = cv2.imread(image_path)
    try: 
        desired_width = simpledialog.askinteger("Input", f"Enter desired width:", minvalue=1)
        desired_height = simpledialog.askinteger("Input", f"Enter desired height:", minvalue=1)
        output_size = (desired_width, desired_height)
        resized_image = cv2.resize(image, output_size, interpolation=cv2.INTER_AREA)
        output_path = os.path.join(output_folder, f"{image_title}_resized_{output_size[0]}x{output_size[1]}.jpg")
        cv2.imwrite(output_path, resized_image)
        # Display the resized image in Tkinter
        resized_image_pil = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)) # Convert to PIL format: BGR --> RGB
        img_display = ImageTk.PhotoImage(resized_image_pil)
        image_label.config(image=img_display)
        image_label.image = img_display
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