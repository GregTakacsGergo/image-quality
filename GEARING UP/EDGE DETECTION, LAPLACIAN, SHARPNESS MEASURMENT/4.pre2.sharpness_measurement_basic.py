import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk


# Function to check sharpness
def is_image_sharp(image_path, threshold=100.0):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image not found or cannot be read")
    
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    return laplacian_var > threshold, laplacian_var

# Function to handle file upload and checking
def upload_and_check():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return

    # Display the uploaded image in Tkinter
    img = Image.open(file_path)
    img.thumbnail((250, 250))
    img = ImageTk.PhotoImage(img)
    image_label.config(image=img)
    image_label.image = img

    try:
        sharp, sharpness_value = is_image_sharp(file_path)
        if sharp:
            messagebox.showinfo("Result", f"The image is sharp enough! (Sharpness: {sharpness_value:.2f})")
        else:
            messagebox.showwarning("Result", f"The image is not sharp enough. (Sharpness: {sharpness_value:.2f})")
    except ValueError as e:
        messagebox.showerror("Error", str(e))

# Tkinter GUI setup

root = tk.Tk()
root.title("Image Sharpness Checker")

# Create and place the image display label
image_label = tk.Label(root)
image_label.pack(pady=10)

# Upload button
upload_button = tk.Button(root, text="Upload Image", command=upload_and_check)
upload_button.pack(pady=20)

root.geometry("300x400")
root.mainloop()
