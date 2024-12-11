import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, Label, Toplevel, Entry, Button, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


class ImageProcessor:
    def __init__(self):
        self.image_path = ""
        self.image_title = ""

    def open_image(self):
        """Open an image file and return its path."""
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if self.image_path:
            self.image_title = os.path.splitext(os.path.basename(self.image_path))[0]
        return self.image_path

    def process_image(self, image_path):
        """Apply grayscale and edge detection on the image."""
        image_grayscale = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image_grayscale is None:
            raise ValueError("Image not found or cannot be read")

        # Sobel gradients
        Gx = cv2.Sobel(image_grayscale, cv2.CV_64F, 1, 0, ksize=3)
        Gy = cv2.Sobel(image_grayscale, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(Gx**2 + Gy**2)
        laplacian = cv2.Laplacian(image_grayscale, cv2.CV_64F)

        return image_grayscale, Gx, Gy, gradient_magnitude, laplacian

    def save_processed_images(self, image_grayscale, Gx, Gy, gradient_magnitude, laplacian, output_path):
        """Save processed images as a single figure."""
        plt.figure(figsize=(20, 5))
        gs = GridSpec(1, 5, width_ratios=[3, 3, 3, 3, 3])

        ax0 = plt.subplot(gs[0])
        ax0.set_title("f(x, y)")
        ax0.imshow(image_grayscale, cmap='gray')

        ax1 = plt.subplot(gs[1])
        ax1.set_title("Gx (\u2202f/\u2202x)")
        ax1.imshow(Gx, cmap='gray')

        ax2 = plt.subplot(gs[2])
        ax2.set_title("Gy (\u2202f/\u2202y)")
        ax2.imshow(Gy, cmap='gray')

        ax3 = plt.subplot(gs[3])
        ax3.set_title("Gradient Magnitude |\u2207f|")
        ax3.imshow(gradient_magnitude, cmap='gray')

        ax4 = plt.subplot(gs[4])
        ax4.set_title("Laplacian (\u22072f)")
        ax4.imshow(laplacian, cmap='gray')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()


class DualImageProcessor(ImageProcessor):
    def __init__(self):
        super().__init__()
        self.image_path1 = ""
        self.image_path2 = ""

    def open_two_images(self):
        """Open two image files."""
        self.image_path1 = self.open_image()
        self.image_path2 = self.open_image()
        return self.image_path1, self.image_path2

    def resize_and_merge_images(self, image_path1, image_path2, output_size, output_path):
        """Resize two images to the same size and merge them side by side."""
        img1 = cv2.imread(image_path1)
        img2 = cv2.imread(image_path2)

        if img1 is None or img2 is None:
            raise ValueError("One or both images could not be read.")

        resized_img1 = cv2.resize(img1, output_size, interpolation=cv2.INTER_AREA)
        resized_img2 = cv2.resize(img2, output_size, interpolation=cv2.INTER_AREA)

        merged_image = np.hstack((resized_img1, resized_img2))
        cv2.imwrite(output_path, merged_image)
        return merged_image


class DualImageApp:
    def __init__(self, root):
        self.root = root
        self.processor = DualImageProcessor()
        self.image_label1 = None
        self.image_label2 = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the Tkinter user interface."""
        self.root.title("Dual Image Processor")

        frame = tk.Frame(self.root, bg="black")
        frame.pack(fill="both", expand=True)

        left_frame = tk.Frame(frame, bg="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        right_frame = tk.Frame(frame, bg="white")
        right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Buttons for opening images
        tk.Button(left_frame, text="Open Image 1", command=self.open_image_1).pack(pady=20)
        self.image_label1 = tk.Label(left_frame, bg="white")
        self.image_label1.pack(pady=10)

        tk.Button(right_frame, text="Open Image 2", command=self.open_image_2).pack(pady=20)
        self.image_label2 = tk.Label(right_frame, bg="white")
        self.image_label2.pack(pady=10)

        # Button for resizing and merging
        tk.Button(self.root, text="Resize and Merge Images", command=self.resize_and_merge).pack(pady=20)

    def open_image_1(self):
        """Open and display the first image."""
        path = self.processor.open_image()
        if path:
            img = Image.open(path)
            img.thumbnail((350, 350))
            img = ImageTk.PhotoImage(img)
            self.image_label1.config(image=img)
            self.image_label1.image = img

    def open_image_2(self):
        """Open and display the second image."""
        path = self.processor.open_image()
        if path:
            img = Image.open(path)
            img.thumbnail((350, 350))
            img = ImageTk.PhotoImage(img)
            self.image_label2.config(image=img)
            self.image_label2.image = img

    def resize_and_merge(self):
        """Resize two images and save them as a merged snapshot."""
        if not self.processor.image_path1 or not self.processor.image_path2:
            messagebox.showerror("Error", "Please select two images before resizing.")
            return

        # Prompt for dimensions
        resize_window = Toplevel(self.root)
        resize_window.title("Enter Resize Dimensions")
        resize_window.geometry("300x200")

        tk.Label(resize_window, text="Width:").pack(pady=5)
        width_entry = Entry(resize_window)
        width_entry.pack(pady=5)

        tk.Label(resize_window, text="Height:").pack(pady=5)
        height_entry = Entry(resize_window)
        height_entry.pack(pady=5)

        def on_submit():
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                output_path = "merged_resized_image.jpg"
                merged_image = self.processor.resize_and_merge_images(
                    self.processor.image_path1, self.processor.image_path2, (width, height), output_path
                )

                # Show success message
                messagebox.showinfo("Success", f"Merged image saved as {output_path}.")

                # Display merged image
                merged_img = Image.fromarray(cv2.cvtColor(merged_image, cv2.COLOR_BGR2RGB))
                merged_img.show()
                resize_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid dimensions.")

        tk.Button(resize_window, text="Submit", command=on_submit).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = DualImageApp(root)
    root.mainloop()
