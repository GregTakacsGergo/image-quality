'''4.pre4.resize_image_oo.py
This code is the object-oriented version of the 4.pre4.resize_image.py.
For further development and optimization the programs need to be scalable and modular.
'''

import os
import cv2
import tkinter as tk
from tkinter import filedialog, Label, messagebox
from PIL import Image, ImageTk

class ImageResizerApp:
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Image Resizer")
        
        self.image_title = ""
        self.image_path = ""
        self.output_folder = "GEARING UP/SEASON1. EDGE DETECTION, LAPLACIAN, SHARPNESS MEASURMENT/resized_images_oo/"
        os.makedirs(self.output_folder, exist_ok=True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components."""
        self.open_button = tk.Button(self.root, text="Open Image", command=self.open_image)
        self.open_button.pack(pady=20)

        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=10)

        self.success_label = Label(self.root, text="")
        self.success_label.pack(pady=30)
    
    def open_image(self):
        """Handle the image opening and display."""
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not self.image_path:
            print("Error: No image selected.")
            return
        
        self.image_title = os.path.splitext(os.path.basename(self.image_path))[0]
        self.display_image(self.image_path, "Original Image")
        self.prompt_resize_dimensions()
    
    def save_image(self, image, output_path):
        #Save an image to the output folder
        if not os.path.exists(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            cv2.imwrite(output_path, image)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            return False   

    def display_image(self, image_path, title):
        """Display an image in the Tkinter window."""
        img = Image.open(image_path)
        img.thumbnail((400, 400))  # Resize for Tkinter display
        img = ImageTk.PhotoImage(img)
        self.image_label.config(image=img, text=title)
        self.image_label.image = img
    
    def prompt_resize_dimensions(self):
        """Prompt the user for the desired resize dimensions."""
        resize_window = tk.Toplevel(self.root)
        resize_window.title("Resize Dimensions")
        resize_window.geometry("300x150")
        
        tk.Label(resize_window, text="Enter width:").pack(pady=5)
        width_entry = tk.Entry(resize_window)
        width_entry.pack(pady=5)

        tk.Label(resize_window, text="Enter height:").pack(pady=5)
        height_entry = tk.Entry(resize_window)
        height_entry.pack(pady=5)

        def submit_dimensions():
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                if width > 0 and height > 0:
                    self.resize_image((width, height)) # pass size as a tuple
                    resize_window.destroy()
                else:
                    messagebox.showerror("Error", "Dimensions must be positive integers.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter integers.")
        
        tk.Button(resize_window, text="Submit", command=submit_dimensions).pack(pady=10)
    
    def resize_image(self, size):
        """Resize the image to the given size and save it."""
        try:
            image = cv2.imread(self.image_path)
            resized_image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
            
            output_path = os.path.join(self.output_folder, f"{self.image_title}_resized_{size[0]}x{size[1]}.jpg")
            self.save_image(resized_image, output_path)
            # Convert resized image for Tkinter display
            resized_image_pil = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
            img_display = ImageTk.PhotoImage(resized_image_pil)
            self.image_label.config(image=img_display, text="Resized Image")
            self.image_label.image = img_display

            self.success_label.config(text=f"Image saved successfully to:\n{output_path}")
            print(f"Image saved successfully to {output_path}")
        except Exception as e:
            print(f"Error resizing image: {e}")
            messagebox.showerror("Error", "An error occurred while resizing the image.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()
