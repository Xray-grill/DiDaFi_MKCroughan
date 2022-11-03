import matplotlib.pyplot as plt
import tifffile as tiff
import numpy as np
import matplotlib.colors as colors



def make_HSV(PATH,SAVE_PATH):
    strength = tiff.imread(PATH+"strength.tif")
    asymmetry = tiff.imread(PATH+"asymmetry.tif")
    theta = tiff.imread(PATH+"theta.tif")

    strength[ strength < 0 ] = 0 # make all sharpened regions of the image 0
    strength = np.interp(strength, (strength.min(), strength.max()), (0, 1)) # Map the strength value to be between 0 and 1. Can be useful to use strength.max()*0.8 or something similar if image is very dark
    
    data_as_hsv = np.zeros(theta.shape + (3,))
    data_as_hsv[..., 0] = theta / (np.pi) # Divide by pi to map angles to be between 0 and 1
    data_as_hsv[..., 1] = asymmetry # asymmetry is already between 0 and 1
    data_as_hsv[..., 2] = strength
    data_as_rbg = colors.hsv_to_rgb(data_as_hsv) # convert to RGB image so matplotlib.pyplot can show image.
    plt.imshow(data_as_rbg)
    plt.show()
    plt.clf()

    tiff.imsave(SAVE_PATH,data_as_rbg)

if __name__ == '__main__':
    PATH = "" # eg "Example_data\\Stage_5-dark_field_retrieval\\"
    SAVE_PATH = "" # eg "Example_data\\Stage-6-HSV_image\\HSV_image.tif" 
    make_HSV(PATH,SAVE_PATH)

