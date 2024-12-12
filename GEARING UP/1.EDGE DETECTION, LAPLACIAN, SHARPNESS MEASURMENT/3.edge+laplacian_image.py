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
        img.thumbnail((350, 350))
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img)
        image_label.image = img

        # Update the window title with the new image title
        root.title(f"Edge Detection Grayscale Image - {image_title}")
    
        # Process the image
        process_image(image_path, image_title)
        
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

    # Apply Laplacian (second derivative)
    laplacian = cv2.Laplacian(image_grayscale, cv2.CV_64F)

    # Display the original function, Gx, Gy, and gradient magnitude
    plt.figure(figsize=(20, 5))
    gs = GridSpec(1, 5, width_ratios=[3,3,3,3,3])

    ax0 = plt.subplot(gs[0])
    ax0.set_title("f(x, y)")
    ax0.imshow(image_grayscale, cmap='gray')

    ax1 = plt.subplot(gs[1])
    ax1.set_title("Gx (∂f/∂x)")
    ax1.imshow(Gx, cmap='gray')

    ax2 = plt.subplot(gs[2])
    ax2.set_title("Gy (∂f/∂y)")
    ax2.imshow(Gy, cmap='gray')
 
    ax3 = plt.subplot(gs[3])
    ax3.set_title("Gradient Magnitude |∇f|")
    ax3.imshow(gradient_magnitude, cmap='gray')
 
    ax4 = plt.subplot(gs[4])
    ax4.set_title("Laplacian (∇²f)")
    ax4.imshow(laplacian, cmap='gray')
    
    plt.tight_layout()
    
    # Read the current counter from a file
    try:
        with open("counter.txt", "r") as file:
            image_number = int(file.read().strip())
    except FileNotFoundError:
        image_number = 1  # Start with 1 if the file doesn't exist

    output_folder = "GEARING UP/1.EDGE DETECTION, LAPLACIAN, SHARPNESS MEASURMENT/edge+laplacian_output"
    os.makedirs(output_folder, exist_ok=True)

    # Save the figure with an incrementing filename
    plt.savefig(f"{output_folder}/edge+laplacian_{image_title}.png", dpi=300, bbox_inches='tight')
    success_label.config(text=f"Image saved successfully to: {output_folder}/edge+laplacian_{image_title}.png")
    print(f"Saved edge detection and laplacian of the image as '{output_folder}/edge+laplacian_{image_title}.png'")

    # Increment the counter and save it back to the file
    with open("counter.txt", "w") as file:
        file.write(str(image_number + 1))

    plt.show()

root = tk.Tk()

button = tk.Button(root, text="Open Image", command=open_and_process_image)
button.pack(pady=20)

image_label = tk.Label(root)
image_label.pack(pady=5)

success_label = Label(root, text="")
success_label.pack(pady=5)
root.mainloop()