# TASK

Take [gray2alpha.py](./src/twat_image/gray2alpha.py) as reference. 

Develop [any2gray.py](./src/twat_image/any2gray.py) as a Fire-based CLI tool. It should do the following. 

## Take an image as input. 

## Convert it to grayscale. 

It should use some general "smart" (perceptual) algorithm to convert the image to grayscale. 

## Normalize the grayscale image. 

1. Normalize the grayscale image so that the brightest parts are white, the darkest parts are black. 

2. Are there some smart algorithms to clean up "noise" in the image, especially in the background? Or alternatively, background removal. For example in OpenCV. 

3. Gauss-curve quantization should happen. Luminance near the extremes should be compressed towards the extremes (white or black), while the middle-range luminance should be kept at a fine gradation. 

4. Optionally use gray2alpha.py to convert the grayscale image to a colored image with an alpha mask (expose the same CLI options). 

## Write the output image to a file. 
