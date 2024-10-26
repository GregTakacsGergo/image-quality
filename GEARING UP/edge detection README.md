**So what is edge detection?**

The primary goal of this step 
Edge detection is a technique used to identify the boundaries of objects in an image. It is a fundamental step in many image processing tasks such as object recognition, object tracking, and image segmentation.

In image processing, the function f(x, y) represents the **intensity** (or brightness) of a pixel at coordinates (x, y) in an image. In grayscale images, intensity values range from 0 (black) to 255 (white) in an 8-bit image format, or from 0.0 to 1.0 if normalized. For color images, f(x, y) could represent the intensity in each color channel (e.g., Red, Green, and Blue).

### Defining the Intensity Function f(x, y) 
1. **Grayscale Image**: 
   - A grayscale image can be thought of as a function f(x, y), where f(x, y) is a single scalar representing the pixel intensity.
   - For an 8-bit grayscale image:
     \[
     f(x, y) ∈ [0, 255]
     \]

### Example Function f(x, y) 

Imagine a small 5x5 grayscale image where f(x, y) contains pixel intensity values from 0 to 255. Here’s a hypothetical intensity matrix for this image:

 $$
f(x, y) =\begin{bmatrix}
  50 & 50 & 80 & 50 & 10 \\\
  50 & 100 & 150 & 100 & 50 \\\
  80 & 150 & 200 & 150 & 80 \\\
  50 & 100 & 150 & 100 & 50 \\\
  10 & 50 & 80 & 50 & 10
\end{bmatrix}
$$

In this matrix:
- f(0, 0) = 10 is the intensity at the top-left corner.
- f(2, 2) = 200 is the intensity at the center, which is the highest value in this example, indicating a bright spot.

### Calculating the First Derivative

To **approximate**  the first derivative, (obviously we will not derivate anything here since f(x, y) is a scalar) we’ll calculate the intensity changes in the \(x\) and \(y\) directions. 
In practice, we do this using convolution with specific operators like the Sobel operator.
The Sobel operator is commonly used to approximate the first derivative. It uses two 3x3 kernels to calculate gradients along the x and y directions:
$$
- **Horizontal (x-axis)**:
Sobel_x = \begin{bmatrix} -1 & 0 & 1 \\\ -2 & 0 & 2 \\\ -1 & 0 & 1 \end{bmatrix}
- **Vertical (y-axis)**:
Sobel_y = \begin{bmatrix} -1 & -2 & -1 \\\ 0 & 0 & 0 \\\ 1 & 2 & 1 \end{bmatrix}
$$

We can then apply these operators to our image to get the first derivative in the x and y directions.
This gives us \( G_x \) and \( G_y \), representing the rate of intensity change across \(x\) and \(y\), respectively.
More about convolution: https://medium.com/@bdhuma/6-basic-things-to-know-about-convolution-daef5e1bc411

1. **Defining the Image**: `f` represents the intensity values for our 5x5 sample "image."
2. **Computing \( G_x \) and \( G_y \)**:
   - `cv2.Sobel(f, cv2.CV_64F, 1, 0, ksize=3)` computes the gradient in the x-direction (horizontal changes).
   - `cv2.Sobel(f, cv2.CV_64F, 0, 1, ksize=3)` computes the gradient in the y-direction (vertical changes).
   ksize is the size of the kernel used for convolution. By default the kernel is 
3. **Calculating the Gradient Magnitude**:
   - We calculate  $$|∇f| = sqrt{G_x^2 + G_y^2}$$, giving us the edge strength at each point in the image.
   
### Result Interpretation
- **Original Intensity Matrix f(x, y)**: Shows the initial intensity values.
- **\( G_x \) and \( G_y \)**: Highlight changes in intensity horizontally and vertically.
- **Gradient Magnitude**: Shows the strength of edges, which are highest where intensity changes rapidly (edges of bright areas).

This approach, used on real images, will provide a detailed edge map, allowing us to locate edges or regions with high-frequency intensity detail effectively.

![Example Edge Detection Output](https://github.com/GregTakacsGergo/image-quality/blob/main/GEARING%20UP/edge_detection_1.png)