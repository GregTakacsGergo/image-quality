# Edge Detection, Laplacian, and Sharpness Measurment
## Introduction

In this project, we will be using Python to perform edge detection, Laplacian, and sharpness measurment on an image. We will be using the following libraries:


### So what is edge detection?

Edge detection is a technique used to identify the boundaries of objects in an image. It is a fundamental step in many image processing tasks such as object recognition, object tracking, and image segmentation.

In image processing, the function f(x, y) represents the **intensity** (or brightness) of a pixel at coordinates (x, y) in an image. In grayscale images, intensity values range from 0 (black) to 255 (white) in an 8-bit image format, or from 0.0 to 1.0 if normalized. For color images, f(x, y) could represent the intensity in each color channel (e.g., Red, Green, and Blue).

### Defining the Intensity Function f(x, y) 
1. **Grayscale Image**: 
   - A grayscale image can be thought of as a function f(x, y), where f(x, y) is a single scalar representing the pixel intensity.
   - For an 8-bit grayscale image:
     \[
     f(x, y) ∈ [0, 255]
     \]

#### Example Function f(x, y) 

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
- f(0, 0) = 50 is the intensity at the top-left corner.
- f(2, 2) = 200 is the intensity at the center, which is the highest value in this example, indicating a bright spot.

### Calculating the First Derivative

To **approximate**  the first derivative, (obviously we will not derive anything here since f(x, y) is a scalar) we’ll calculate the intensity changes in the \(x\) and \(y\) directions. 
In practice, we do this using convolution with specific operators like the Sobel operator.
The Sobel operator is commonly used to approximate the first derivative. It uses two 3x3 kernels to calculate gradients along the x and y directions:

Horizontal (x-axis):

$$
Sobel_x = \begin{bmatrix} 
   -1 & 0 & 1 \\\
   -2 & 0 & 2 \\\
   -1 & 0 & 1 
\end{bmatrix}
$$

Vertical (y-axis):

$$
Sobel_y = \begin{bmatrix} 
-1 & -2 & -1 \\\
0 & 0 & 0 \\\
1 & 2 & 1 
\end{bmatrix}
$$

We can then apply these operators to our image to get the first derivative in the x and y directions.
This gives us \( G_x \) and \( G_y \), representing the rate of intensity change across \(x\) and \(y\), respectively.
More about convolution: https://medium.com/@bdhuma/6-basic-things-to-know-about-convolution-daef5e1bc411.

1. **Defining the Image**: `f` represents the intensity values for our 5x5 sample "image."
2. **Computing \( G_x \) and \( G_y \)**:
   - `cv2.Sobel(f, cv2.CV_64F, 1, 0, ksize=3)` computes the gradient in the x-direction (horizontal changes).
   - `cv2.Sobel(f, cv2.CV_64F, 0, 1, ksize=3)` computes the gradient in the y-direction (vertical changes).
   ksize is the size of the kernel used for convolution. By default the kernel is 3x3.
3. **Calculating the Gradient Magnitude**:
   - We calculate: |∇f| = $$\sqrt{G_x^2 + G_y^2}$$
    giving us the edge strength at each point in the image.
   
### Result Interpretation
- **Original Intensity Matrix f(x, y)**: Shows the initial intensity values.
- **G_x  and  G_y**: Highlight changes in intensity horizontally and vertically.
- **Gradient Magnitude**: Shows the strength of edges, which are highest where intensity changes rapidly (edges of bright areas).

This approach, used on real images, will provide a detailed edge map, allowing us to locate edges or regions with high-frequency intensity detail effectively.

*see: https://github.com/GregTakacsGergo/image-quality/blob/main/GEARING%20UP/EDGE%20DETECTION%2C%20LAPLACIAN%2C%20SHARPNESS%20MEASURMENT/1.edge_detection_matrix.py*

![Example Edge Detection Output](https://github.com/GregTakacsGergo/image-quality/blob/main/GEARING%20UP/EDGE%20DETECTION%2C%20LAPLACIAN%2C%20SHARPNESS%20MEASURMENT/resources/edge_detection_1.png)

In the next step we will apply Laplacian operator on the f matrix to determine sharpness of the image. Later we will determine the *laplacian_var* i.e. the variance of the laplacian of the image, which will give us an idea of the sharpness of the image.
This edge detection step is not strictly necessary for image quality assessment, but it is a crucial step in many image processing tasks, and understanding overall sharpness measurement process.

### APLYING EDGE DETECTION ON A REAL IMAGE

*see: https://github.com/GregTakacsGergo/image-quality/blob/main/GEARING%20UP/EDGE%20DETECTION%2C%20LAPLACIAN%2C%20SHARPNESS%20MEASURMENT/2.edge_detection_image.py*

Edge Detection Output of a cool car:

![Edge Detection on a cool car:](https://github.com/GregTakacsGergo/image-quality/blob/main/GEARING%20UP/EDGE%20DETECTION%2C%20LAPLACIAN%2C%20SHARPNESS%20MEASURMENT/resources/edge_detection_grayscale_image_opel.png)

The edges of the car are clearly visible in the output. 


### Laplacian Operator

The Laplacian, often denoted as ∇²f, highlights areas of *rapid intensity change* in an image, making it useful for edge detection and feature extraction. In edge detection, it identifies points where intensity changes most, typically at edges, or boundaries within an image. Mathematically, the Laplacian of an image f is defined as:

$$
\begin{align*}
\nabla^2 f(x,y) &= \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2} \\
\end{align*}
$$

This second derivative can detect peaks or valleys in intensity—places where brightness changes suddenly (e.g., edges). At these points, the Laplacian produces large positive or negative values.
To implement this, a 3x3 kernel approximates the second derivative across the image by convolving (filtering) it with the Laplacian kernel. The most commonly used kernel for the Laplacian in a 3x3 form is:

$$
     \begin{bmatrix}
     0 & 1 & 0 \\\
     1 & -4 & 1 \\\
     0 & 1 & 0
     \end{bmatrix}
$$

These kernels detect changes in both x and y directions in a single operation (non-directional), making them efficient for edge detection.
Since the Laplacian can produce both positive and negative values, *it captures edges as points where the pixel value crosses zero*, marking a transition in intensity.

### Programming Implementation of the Laplacian

*see: https://github.com/GregTakacsGergo/image-quality/blob/main/GEARING%20UP/EDGE%20DETECTION%2C%20LAPLACIAN%2C%20SHARPNESS%20MEASURMENT/3.edge%2Blaplacian_image.py*

In code, we apply the Laplacian operator using OpenCV’s `cv2.Laplacian()` function, which computes the second derivative across the image. Here’s how to integrate it into the edge detection workflow:  
```python
import cv2 
...
image_grayscale=cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
laplacian = cv2.Laplacian(image_grayscale, cv2.CV_64F)   
```
The `cv2.Laplacian()` function takes two arguments: the input image and the type of output. In this case, we use `cv2.CV_64F` to get a floating-point output. When calculating the Laplacian (a second derivative), we detect both positive and negative changes in intensity. These changes represent different types of transitions:
- Positive values indicate a transition from dark to bright (a rise in intensity).
- Negative values indicate a transition from bright to dark (a drop in intensity).
If we used an 8-bit unsigned integer type like `cv2.CV_8U`, which only supports values between 0 and 255, negative values would be clipped (converted to 0). This would distort the result and lose important information about the edges.
With floating-point values, we have more flexibility for post-processing, such sharpness measurement, or further operations on the detected edges.

![frank:](https://github.com/GregTakacsGergo/image-quality/blob/main/GEARING%20UP/EDGE%20DETECTION%2C%20LAPLACIAN%2C%20SHARPNESS%20MEASURMENT/resources/edge_detection_grayscale_image_frank.png)

### Sharpness Measurement 
The Laplacian variance can be used to measure the sharpness of an image. The variance of the Laplacian measures the amount of noise present in the image, which can be used to determine the overall quality of the image. Noise, in the context of Laplacian variance-based sharpness detection means the following. Noise is a random variation in the image intensity that can be caused by a variety of factors, such as camera shake, motion blur, or other image artifacts.
- **High Variance** indicates strong edges with clear transitions between light and dark regions, pointing to a detailed image.
High Variance Due to Noise: Noise also creates intensity fluctuations, leading to an artificially high Laplacian variance. This can mislead sharpness detection algorithms, as high variance here doesn’t always equate to actual image detail. A high variance indicates a high degree of noise, while a low variance indicates a low degree of noise. A sharper image will have a lower variance, while a blurrier image will have a higher variance.

```python
laplacian_var = cv2.Laplacian(image_grayscale, cv2.CV_64F).var()
```
We then calculate the variance of the Laplacian using the `var()` method, which returns the variance of the Laplacian values across the image. This value later can be used to measure the **sharpness** of the image.

### Result Interpretation
Here in the 4.pre5.resizer+sharpness.py program (which gets two images -- shows them side by side with their original size -- resizes them to the desired size -- calculates the sharpness of the resized images using the Laplacian variance method) we can see some in my opinion interesting results:

![sharpness_difference:](https://github.com/GregTakacsGergo/image-quality/blob/main/GEARING%20UP/1.EDGE%20DETECTION%2C%20LAPLACIAN%2C%20SHARPNESS%20MEASURMENT/resources/sharpness_difference.jpg)

- First of all, normalization (in size) does not affect sharpness measurement at all, at least with the methods used here. The sharpness of the original image is the same as the sharpness of the resized image. 
- Secondly the first image is clearly less "sharp" than the second one. Of course we understand the concepts so far but still this result is a little bit surprising. One would expect that the first image will have lower sharpness, since it's blurry, and has low resolution. Still it seems that the overall noise and high contrast in color makes it less sharp. 
Still if we compare an intentionally blurred image with it's original version, we get the expected result:

![sharpness_difference_agama:](https://github.com/GregTakacsGergo/image-quality/blob/main/GEARING%20UP/1.EDGE%20DETECTION%2C%20LAPLACIAN%2C%20SHARPNESS%20MEASURMENT/resources/agama_sharpness_comparison.jpg)

note: we added a few more params to the laplacian_var calculation to get a better result: 
```python
laplacian_var = cv2.Laplacian(image_grayscale, cv2.CV_16S, ksize=5, scale=1, delta=0).var() 
```
This is because the default values for the `ksize`, `scale`, and `delta` parameters are not optimal for sharpness measurement. The `ksize` parameter should be set to 5 to get a better approximation of the Laplacian operator. The `scale` parameter should be set to 1 to get the absolute value of the Laplacian, and the `delta` parameter should be set to 0 to get the variance of the Laplacian.

#### One bit of Conclusion:
Sharnpness measurement is not the best way to measure image quality. So far we know that it works on the same images, but it might not be the best way to measure image quality in real-world applications. It is important to understand the concepts of edge detection, Laplacian, and sharpness measurement, and to use them in combination to achieve better image quality assessment. 
In the near future we'll introduce resolution measuremnt too, and add more functionallities to the dual_resizer_ application package.
