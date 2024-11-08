
## Gearing up for the project ##
The GEARING UP folder contains programs that were the essential steps to achieve the fully functional image_quality_checker little software. 
These programs (mostly python scripts) are pieces of the greater picture, and can be used to better understand the overall process 
and how it can be broken down into smaller, more manageable tasks.
- first part: EDGE DETECTION, LAPLACIAN, SHARPNESS MEASURMENT:
    These programs are used to detect edges in an image, calculate the Laplacian and sharpness of the image. Initially the end result, the sharpness as a number ie. /*laplacian variance*, is used to determine the quality of the image. We can distinguish between images with high laplacian variance and low laplacian variance as having high and low quality respectively. 
    Using these methods, in the end of the first part of the project we can organize a set of images into 3 categories based on their laplacian variance:
    - High laplacian variance [200+]: theoretically, high quality images
    - Medium laplacian variance [100-199]: medium.
    - Low laplacian variance [0-99]: low quality images.
    It is going to be interesting to see, if thees categories a are accurately reflecting the actual quality of the images.
    

