#Code written by Michelle K Croughan, Monash University Australia, 2022
#This can be found at https://github.com/Xray-grill/DiDaFi_MKCroughan
#Any research output utilising this code must be open source and reference this published article: <DOI of article>

import tifffile as tiff

def flat_and_dark_images(flat,dark,image,save_name): #Compute and save flad and darked image
    fad = (image-dark)/(flat-dark) #Compute flat and dark image
    tiff.imsave(save_name,fad) #Save image
    return

if __name__ == '__main__':
    FLAT = tiff.imread("") #Include path to flat image eg C:\\Users\\michelle\\Data\\Flat_20ms_average.tif
    DARK = tiff.imread("") #Include path to dark image eg C:\\Users\\michelle\\Data\\Dark_20ms_average.tif
    IMAGE = tiff.imread("") #Include path to dark image eg C:\\Users\\michelle\\Data\\Image_20ms.tif
    SAVE_NAME = "" #The folder and file name for your flat-and-darked image eg C:\\Users\\michelle\\Data\\Image_20ms_FAD.tif

    flat_and_dark_images(FLAT,DARK,IMAGE,SAVE_NAME) #Call function to compute and save flat and darked image

