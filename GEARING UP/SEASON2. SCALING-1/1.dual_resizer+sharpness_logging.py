'''SEASON2. SCALING-11.pre1.dual_resizer+sharpness_logging.py

'''

import os
import cv2
import tkinter as tk
from tkinter import filedialog, Label, Toplevel, Entry, Button, Frame, messagebox
from PIL import Image, ImageTk
import numpy as np
import logging

# Logging configuration
log_directory = "GEARING UP/SEASON2. SCALING-1/logs"  # Specify the log directory
os.makedirs(log_directory, exist_ok=True)  # Create the directory if it doesn't exist

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    filename=os.path.join(log_directory, "1.dual_resizer+sharpness_logging.log"), 
                    filemode="w")
class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.image_path = ""
        self.image_title = ""
        self.output_folder = "GEARING UP/SEASON2. SCALING-1/1.output/"
        os.makedirs(self.output_folder, exist_ok=True)
        logging.info("Dual Image Resizer and sharpness measurer started")

    def open_image(self, label):
        #Open an image file and display it in the UI
        logging.info("Attempting to open an image file")
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not self.image_path:
            logging.warning("No image selected")
            messagebox.showerror("Error", "No image selected.")
            return

        try:
            self.image_title = os.path.splitext(os.path.basename(self.image_path))[0]
            img = Image.open(self.image_path)
            img_tk = ImageTk.PhotoImage(img)
            label.config(image=img_tk)
            label.image = img_tk
            logging.info(f"Image {self.image_title} opened successfully")
            return self.image_path
        except Exception as e:
            logging.error(f"Failed to open image {self.image_title}. Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")
    
    def save_image(self, image, output_path):
        #Save an image to the output folder
        logging.info(f"Attempting to save image {self.image_title} to {output_path}")
        if not os.path.exists(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            logging.debug(f"Output folder {os.path.dirname(output_path)} created")
        try:
            cv2.imwrite(output_path, image)
            logging.info(f"Image {self.image_title} saved successfully to {output_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to save image {self.image_title} to {output_path}. Error: {str(e)}")    
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            return False    
        
    def resize_image(self, image_path, output_size):
        logging.info(f"Resizing image: {image_path} to size: {output_size}")
        try:
            image = cv2.imread(image_path)
            resized_image = cv2.resize(image, output_size, interpolation=cv2.INTER_AREA)
            logging.info(f"Image resized successfully: {image_path}")
            return resized_image
        except Exception as e:
            logging.error(f"Failed to resize image: {image_path}. Error: {e}")
            messagebox.showerror("Error", f"Failed to resize image: {str(e)}")
            return None

class DualImageResizerApp(ImageResizerApp):
    def __init__(self, root):
        super().__init__(root)
        self.root.title("Dual Image Resizer and sharpness measurer")
        self.image_path1 = ""
        self.image_path2 = ""
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        logging.info("Dual Image Resizer and sharpness measurer closed")
        self.root.destroy()

    def setup_ui(self):
        #Set up the UI components for two images.
        # Create a frame for dividing the window into two columns
        logging.info("Setting up the UI components")
        frame = Frame(self.root, bg="black")
        frame.pack(fill="both", expand=True)

        # Left column
        left_frame = Frame(frame, bg="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.open_button1 = Button(left_frame, text="Open Image 1", command=lambda: self.open_image_1())
        self.open_button1.pack(pady=20)

        #These are needed because the UI window became unhandlable on large images
        self.image_frame1 = Frame(left_frame, bg="white", width=900, height=600)
        self.image_frame1.pack_propagate(False)
        self.image_frame1.pack(pady=10)
        self.image_label1 = Label(self.image_frame1, bg="white")
        self.image_label1.pack(pady=10)

        self.sharpness_button1 = Button(left_frame, text="Measure Sharpness", command=lambda: self.measure_sharpness(self.image_path1, self.success_label_left))
        self.sharpness_button1.pack(pady=5)

        self.success_label_left = Label(left_frame, text="")
        self.success_label_left.pack(pady=25)

        # Right column
        right_frame = Frame(frame, bg="white")
        right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.open_button2 = Button(right_frame, text="Open Image 2", command=lambda: self.open_image_2())
        self.open_button2.pack(pady=20)
        
        self.image_frame2 = Frame(right_frame, bg="white", width=900, height=600)
        self.image_frame2.pack_propagate(False)
        self.image_frame2.pack(pady=10)
        self.image_label2 = Label(self.image_frame2, bg="white")
        self.image_label2.pack(pady=10)

        self.sharpness_button2 = Button(right_frame, text="Measure Sharpness", command=lambda: self.measure_sharpness(self.image_path2, self.success_label_right))
        self.sharpness_button2.pack(pady=5)

        self.success_label_right = Label(right_frame, text="")
        self.success_label_right.pack(pady=25)

        # Resize button at the bottom
        self.resize_button = Button(self.root, text="Resize Images", command=self.prompt_resize_dimensions)
        self.resize_button.pack(pady=20)

        self.success_label = Label(self.root, text="")
        self.success_label.pack(pady=30)

    def open_image_1(self):
        logging.info("Opening image 1.")
        self.image_path1 = self.open_image(self.image_label1)

    def open_image_2(self):
        logging.info("Opening image 2.")
        self.image_path2 = self.open_image(self.image_label2)

    def merge_images(self, image1, image2):
        logging.info("Merging two images.")
        merged_image = np.hstack((image1, image2))
        return merged_image 

    def prompt_resize_dimensions(self):
        #Create a pop-up window to input desired resize dimensions for both images.
        if not self.image_path1 or not self.image_path2:
            logging.warning("Resize attempted without both images loaded.")
            messagebox.showerror("Error", "Please select both images before resizing.")
            return

        logging.info("Prompting user for resize dimensions.")
        resize_window = Toplevel(self.root)
        resize_window.title("Enter Resize Dimensions")
        resize_window.geometry("300x200")

        Label(resize_window, text="Width:").pack(pady=5)
        width_entry = Entry(resize_window)
        width_entry.pack(pady=5)

        Label(resize_window, text="Height:").pack(pady=5)
        height_entry = Entry(resize_window)
        height_entry.pack(pady=5)

        def on_submit():
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                self.resize_and_display_images((width, height))
                resize_window.destroy()
            except ValueError as e:
                logging.error(f"Invalid resize dimensions entered. Error: {str(e)}")
                messagebox.showerror("Error", "Please enter valid dimensions.")

        submit_button = Button(resize_window, text="Submit", command=on_submit)
        submit_button.pack(pady=10)

    def resize_and_display_images(self, output_size):
        #Resize both images and update the display.
        logging.info(f"Resizing images to size: {output_size}")
        try:
            resized_image1 = self.resize_image(self.image_path1, output_size)    
            #display image1
            if resized_image1 is not None:
                resized_image1_pil = Image.fromarray(cv2.cvtColor(resized_image1, cv2.COLOR_BGR2RGB))
                img_tk1 = ImageTk.PhotoImage(resized_image1_pil)
                self.image_label1.config(image=img_tk1)
                self.image_label1.image = img_tk1
                logging.info(f"Image 1 resized to size: {output_size}")
            else:
                logging.warning(f"Image 1 resizing failed: {self.image_path1}")

            resized_image2 = self.resize_image(self.image_path2, output_size)
            #display image2
            if resized_image2 is not None:
                resized_image2_pil = Image.fromarray(cv2.cvtColor(resized_image2, cv2.COLOR_BGR2RGB))
                img_tk2 = ImageTk.PhotoImage(resized_image2_pil)
                self.image_label2.config(image=img_tk2)
                self.image_label2.image = img_tk2
                logging.info(f"Image 2 resized to size: {output_size}")
            else:
                logging.warning(f"Image 2 resizing failed: {self.image_path2}")    

            #save merged images
            if resized_image1 is not None and resized_image2 is not None:
                merged_image = self.merge_images(resized_image1, resized_image2)
                output_path = os.path.join(
                    self.output_folder,
                    f"{os.path.splitext(os.path.basename(self.image_path))[0]}_resized_{output_size[0]}x{output_size[1]}.jpg")
                if self.save_image(merged_image, output_path):
                    self.success_label.config(text=f"Image saved successfully to:\n{output_path}")
                    logging.info(f"Image saved successfully to {output_path}")
                else:
                    self.success_label.config(text=f"Image saving failed.")
                    logging.error(f"Image saving failed to {output_path}")
                print(f"Image saved successfully to {output_path}")
            else:
                logging.warning("Merged image creation skipped due to failed resizing of one or both images.")

        except Exception as e:
            logging.exception(f"Failed to resize and display images. Error: {str(e)}")

        logging.info("Images resized and displayed successfully.")        

    def measure_sharpness(self, image_path, success_label):
        if not image_path:
            logging.warning("Sharpness measurement attempted without an image.")
            messagebox.showerror("Error", "Please open an image first.")
            return
        
        logging.info(f"Measuring sharpness of image: {image_path}")
        try:
            image_grayscale = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image_grayscale is None:
                logging.warning(f"Failed to read grayscale image")
                messagebox.showerror("Error", "Image not found or cannot be read.") 


            laplacian_var = cv2.Laplacian(image_grayscale, cv2.CV_16S, ksize=5, scale=1, delta=0).var()
            success_label.config(text=f"Sharpness: {laplacian_var:.2f}")
            logging.info(f"Sharpness of {image_path} measured successfully. Sharpness value: {laplacian_var:.2f}")
        except Exception as e:
            logging.exception(f"Failed to measure sharpness of image: {image_path}. Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to measure sharpness: {str(e)}")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = DualImageResizerApp(root)
    root.mainloop()
