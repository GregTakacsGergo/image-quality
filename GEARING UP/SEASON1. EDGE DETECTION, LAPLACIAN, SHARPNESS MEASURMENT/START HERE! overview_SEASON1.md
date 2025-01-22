This document is an overview of the first season of this project. I think this is useful because it might not be clear for those who want to understand what this whole project is for... 
To be honest I have to admit that when i started building this project back in October 2024, I didn't have a clear idea of what I was trying to achieve. 
I was learning and testing new techniques and tools, on the go, and I wanted to develop a project that almost resembled a "professional" one.  
Slowly adding each new feature, I think I got a bit lost in the details and I didn't have a clear idea of what I was trying to achieve. Thats why I decided, that the first two or three seasons of this project will be dedicated literally to gear up for so called "final product". Try and test every feature that might be useful later, and then I can decide what to implement.  

So let's start with the first part of the project (i really love to call it "season" :D ):
- FIRST PART: EDGE DETECTION, LAPLACIAN, SHARPNESS MEASURMENT:
    For more technical details, please check out the THESIS document. Here I will only  try to briefly describe the main steps of this part, and explain what these scripts actually do. So lets dive in! 

    These programs are used to detect edges in an image, calculate the Laplacian and sharpness of the image. Initially the end result, the sharpness as a number ie. /*laplacian variance*, is used to determine the quality of the image. We can distinguish between images with high laplacian variance and low laplacian variance as having high and low quality respectively. Please go to THESIS document for more details about these terms: edge, gradient, Laplacian, sharpness, laplacian variance, etc. 

    The first three scripts: 1.edge_detection_matrix, 2.edge_detection_image, 3.edge+laplacian_image were used to get to a result, where we can see all these techniques used on real images. And a lot of background work for correctly saving these results, naming conventions etc...
    Then when we get to the *4.laplacian+sharnpness_image* we already have the experimentation with sharpness measurement implemented(4.pre1 and 4.pre2). 

    So let's try runing these programs on a sample image and see the results. I am using *4.laplacian+sharnpness_image.py* here.

        ![agama-is-sharp:](https://github.com/GregTakacsGergo/image-quality/blob/main/GEARING%20UP/1.EDGE%20DETECTION%2C%20LAPLACIAN%2C%20SHARPNESS%20MEASURMENT/resources/agama-is-sharp.jpg)

        ![agama-not-sharp:](https://github.com/GregTakacsGergo/image-quality/blob/main/GEARING%20UP/1.EDGE%20DETECTION%2C%20LAPLACIAN%2C%20SHARPNESS%20MEASURMENT/resources/agama-not-sharp.jpg)
        
    But even before we could correctly measure these images, we have to run some **normalization and preprocessing** steps to make them suitable for the edge detection and laplacian calculation. 
    1. a. We can compare the same picture (one being blurred and the other being sharp... already done ), b. and we can compare two different pictures (this is where we have to normalize them to the same size, due to different resolutions).
    2. We might consider normalizing other aspects of the images, such as the color balance, contrast, brightness, etc. But for now let's assume these factors don't affect the quality of the image. I know this is a very naive and probably too pragmatic approach, but the complexity of the project would scale exponentially very fast if we tried to consider all these factors at once.
       -  1.b.  So let's compare two different sized pictures. In this process *4.pre4.resize_image.py* I will first resize the images to a common size (say 400x300) and then apply the same sharpness measurement process to both of them.