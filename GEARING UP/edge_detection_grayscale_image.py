import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, Label
from PIL import Image, ImageTk

image_title = ""

def open_and_process_image():
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
    image_title = os.path.splitext(os.path.basename(image_path))[0]

    try:
        # Display the uploaded image in Tkinter
        img = Image.open(image_path)
        img.thumbnail((250, 250))
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img)
        image_label.image = img

        # Process the image
        process_image(image_path, image_title)
        success_label.config(text=f"Image saved successfully")
    except FileNotFoundError:
        print("Error: Could not find the image file.")


def process_image(image_path, image_title):
    image_grayscale=cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image_grayscale is None:
        print("Error: Could not read the image.")
        return
    
    # Use OpenCV's Sobel operator to compute gradients along x and y directions
    Gx = cv2.Sobel(image_grayscale, cv2.CV_64F, 1, 0, ksize=3)  # Gradient in x direction
    Gy = cv2.Sobel(image_grayscale, cv2.CV_64F, 0, 1, ksize=3)  # Gradient in y direction

    # Compute the gradient magnitude
    gradient_magnitude = np.sqrt(Gx**2 + Gy**2)

    # Display the original function, Gx, Gy, and gradient magnitude
    plt.figure(figsize=(12, 3))
    plt.subplot(1, 4, 1)
    plt.title("f(x, y)")
    plt.imshow(image_grayscale, cmap='gray')
    plt.colorbar()

    plt.subplot(1, 4, 2)
    plt.title("Gx (∂f/∂x)")
    plt.imshow(Gx, cmap='gray')
    plt.colorbar()

    plt.subplot(1, 4, 3)
    plt.title("Gy (∂f/∂y)")
    plt.imshow(Gy, cmap='gray')
    plt.colorbar()
        
    plt.subplot(1, 4, 4)
    plt.title("Gradient Magnitude |∇f|")
    plt.imshow(gradient_magnitude, cmap='gray')
    plt.colorbar()
    # Read the current counter from a file
    try:
        with open("counter.txt", "r") as file:
            image_number = int(file.read().strip())
    except FileNotFoundError:
        image_number = 1  # Start with 1 if the file doesn't exist

    output_folder = "GEARING UP/edge_detection_output"
    os.makedirs(output_folder, exist_ok=True)

    # Save the figure with an incrementing filename
    plt.savefig(f"{output_folder}/edge_detection_grayscale_image_{image_title}.png", dpi=300, bbox_inches='tight')

    # Increment the counter and save it back to the file
    with open("counter.txt", "w") as file:
        file.write(str(image_number + 1))

    plt.show()

root = tk.Tk()
root.title(f"Edge Detection Grayscale Image - {image_title}")
image_label = tk.Label(root)
image_label.pack(pady=10)

button = tk.Button(root, text="Open Image", command=open_and_process_image)
button.pack(pady=20)

success_label = Label(root, text="")
success_label.pack(pady=30)
root.mainloop()