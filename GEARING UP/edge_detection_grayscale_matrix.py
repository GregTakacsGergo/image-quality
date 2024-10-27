import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Define a sample 5x5 image to simulate our function f(x, y)
f = np.array([
    [50, 50, 80, 50, 10],
    [50, 100, 150, 100, 50],
    [80, 150, 200, 150, 80],
    [50, 100, 150, 100, 50],
    [10, 50, 80, 50, 10]
], dtype=np.uint8)

# Use OpenCV's Sobel operator to compute gradients along x and y directions
Gx = cv2.Sobel(f, cv2.CV_64F, 1, 0, ksize=3)  # Gradient in x direction
Gy = cv2.Sobel(f, cv2.CV_64F, 0, 1, ksize=3)  # Gradient in y direction

# Compute the gradient magnitude
gradient_magnitude = np.sqrt(Gx**2 + Gy**2)

# Display the original function, Gx, Gy, and gradient magnitude
plt.figure(figsize=(12, 3))
plt.subplot(1, 4, 1)
plt.title("f(x, y)")
plt.imshow(f, cmap='gray')
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

output_folder = "edge_detection_images"
os.makedirs(output_folder, exist_ok=True)

# Save the figure with an incrementing filename
plt.savefig(f"{output_folder}/edge_detection_grayscale_matrix_{image_number}.png", dpi=300, bbox_inches='tight')

# Increment the counter and save it back to the file
with open("counter.txt", "w") as file:
    file.write(str(image_number + 1))

plt.show()
