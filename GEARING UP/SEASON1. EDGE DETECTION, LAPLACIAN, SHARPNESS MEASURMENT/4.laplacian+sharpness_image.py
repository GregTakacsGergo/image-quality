import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import tkinter as tk
from tkinter import filedialog, Label
from PIL import Image, ImageTk

image_title = ""
image_path = ""

def open_and_process_image():
    global image_title, image_path
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
    
        process_image(image_path, image_title)
        success_label.config(text=f"Image saved successfully")
    except FileNotFoundError:
        print("Error: Could not find the image_grayscale file.")

def process_image(image_path, image_title):
    image_grayscale=cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image_grayscale is None:
        print("Error: Could not read the image_grayscale.") 
        return
    # Use OpenCV's Sobel operator to compute gradients along x and y directions
    Gx = cv2.Sobel(image_grayscale, cv2.CV_64F, 1, 0, ksize=3)  
    Gy = cv2.Sobel(image_grayscale, cv2.CV_64F, 0, 1, ksize=3)  
    gradient_magnitude = np.sqrt(Gx**2 + Gy**2)
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

    output_folder = "GEARING UP/SEASON1. EDGE DETECTION, LAPLACIAN, SHARPNESS MEASURMENT/edge+laplacian+sharpness_output"
    os.makedirs(output_folder, exist_ok=True)

    plt.savefig(f"{output_folder}/edge+laplacian+sharpness_{image_title}.png", dpi=300, bbox_inches='tight')
    print(f"Saved edge detection and laplacian of the image_grayscale as '{output_folder}/edge+laplacian+sharpness_{image_title}.png'")

    plt.show()

def measure_sharpness(threshold):
    if not image_path:
        tk.messagebox.showerror("Error", "Please Open and Process an image first.")
        return
    image_grayscale = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image_grayscale is None:
        raise ValueError("Image not found or cannot be read")
    laplacian_var = cv2.Laplacian(image_grayscale, cv2.CV_64F).var()
    return laplacian_var > threshold, laplacian_var

def prompt_sharpness_threshold_input():
    if not image_path:
        tk.messagebox.showerror("Error", "Please Open and Process an image first.")
        return      
    #Creating new window for sharpness threshold input
    sharpness_threshold_window = tk.Toplevel(root)
    sharpness_threshold_window.title("Sharpness Threshold")
    sharpness_threshold_window.geometry("300x100")
    #Creating label for sharpness threshold input
    sharpness_threshold_label = tk.Label(sharpness_threshold_window, text="Enter sharpness threshold:")
    sharpness_threshold_label.pack(pady=5)
    #Creating entry for sharpness threshold input
    sharpness_threshold_entry = tk.Entry(sharpness_threshold_window)
    sharpness_threshold_entry.pack(pady=5)

    def measure_sharpness_with_threshold():
        
        try:      
            threshold = float(sharpness_threshold_entry.get())
            is_sharp, laplacian_var = measure_sharpness(threshold)
            sharpness_message = (f"The image is sharp enough with a Laplacian variance of {laplacian_var:.2f}" 
                                 if is_sharp else
                                 f"The image is not sharp enough with a Laplacian variance of {laplacian_var:.2f}")
            tk.messagebox.showinfo("Sharpness Result", sharpness_message)
            sharpness_threshold_window.destroy()
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid input. Please enter a valid treshold value.") 
    submit_button = tk.Button(sharpness_threshold_window, text="Submit", command=measure_sharpness_with_threshold)
    submit_button.pack(pady=5)

root = tk.Tk()

open_and_process_button = tk.Button(root, text="Open and Process an Image", command=open_and_process_image)
open_and_process_button.pack(pady=20)

measure_sharpness_button = tk.Button(root, text="Measure Sharnpess", command=prompt_sharpness_threshold_input)
measure_sharpness_button.pack(pady=25)

image_label = tk.Label(root)
image_label.pack(pady=10)

success_label = Label(root, text="")
success_label.pack(pady=30)
root.mainloop()