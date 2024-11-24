
## Gearing up for the project ##
The GEARING UP folder contains programs that were the essential steps to achieve the fully functional image_quality_checker software. 
These programs (mostly python scripts) are pieces of the greater picture, and can be used to better understand the overall process 
and how it can be broken down into smaller, more manageable tasks.
- FIRST PART: EDGE DETECTION, LAPLACIAN, SHARPNESS MEASURMENT:
    These programs are used to detect edges in an image, calculate the Laplacian and sharpness of the image. Initially the end result, the sharpness as a number ie. /*laplacian variance*, is used to determine the quality of the image. We can distinguish between images with high laplacian variance and low laplacian variance as having high and low quality respectively. 
    Using these methods, in the end of the first part of the project we can organize a set of images into 3 categories based on their laplacian variance:
    - High laplacian variance [200+]: theoretically, high quality images
    - Medium laplacian variance [100-199]: medium.
    - Low laplacian variance [0-99]: low quality images.
    It is going to be interesting to see, if thees categories are accurately reflecting the actual quality of the images. So let's try runing these programs on asample image and see the results.
        ![agama-sharp:]
    But even before we could correctly measure these images, we have to run some **normalization and preprocessing** steps to make them suitable for the edge detection and laplacian calculation. 
    1. a. We can compare the same picture (one being blurred and the other being sharp), b. and we can compare two different pictures (this is where we have to normalized them to the same size, due to different resolutions).
    2. We might consider normalizing other aspects of the images, such as the color balance, contrast, brightness, etc. But for now let's assume these factors don't affect the quality of the image. I know this is a very naive and probably too pragmatic approach, but the complexity of the project would scale exponentially very fast if we tried to consider all these factors at once.
       -  1.a. 