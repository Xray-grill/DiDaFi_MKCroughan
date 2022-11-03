#Code written by Michelle K Croughan, Monash University Australia, 2022
#This code and license can be found at https://github.com/Xray-grill/DiDaFi_MKCroughan
#Any research output utilising this code must reference this published article: <DOI of article>

import tifffile as tiff
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import correlate
import os
from dask import delayed, compute
from dask.diagnostics import Profiler
from dask.diagnostics import ProgressBar
from dask import config

def coefficient_images(GRID_IMAGE_PATH,SAMPLE_AND_GRID_IMAGE_PATH,SAVE_PATH,PERIOD,KERNEL_SIZE,DASK):
    def correlation_expression(x_y_coordinates,c_0,c_1,c_2,c_3,c_4,phase_1,phase_2):
        # Define function to fit to auto-correlation of I_g and cross-correlation of I_g and I_sg. Allow phase of trig functions to be a free parameter.
        x2d, y2d = x_y_coordinates
        return c_0 + c_1*np.cos((2. *np.pi *x2d)/PERIOD +phase_1)+ \
            c_2*np.cos((2.*np.pi *y2d)/PERIOD +phase_2)+ \
            c_3*np.cos((2. *np.pi *(x2d-y2d))/PERIOD +phase_1-phase_2)+ \
            c_4*np.cos((2. *np.pi *(x2d+y2d))/PERIOD + phase_1+phase_2)

    def compute_coefficents(kernel_row,window_row,sample_in_x, kernel_size, kernel_size_half):

        c_part = np.empty((sample_in_x,5))
        for xx in range(sample_in_x):
            # Pull out sub arrays needed to perform correlations
            kernel = kernel_row[kernel_size_half:kernel_size_half+
                kernel_size,xx+kernel_size_half:xx+kernel_size_half+kernel_size] 
            window =window_row[:,xx:xx+2*kernel_size] 

            correlation = correlate(window,kernel,mode = 'valid')
            
            #Make 2d meshgrid the size of the subarrays in autocorrelation and cross correlation space
            x = np.linspace(0, kernel_size,kernel_size+1)
            y = np.linspace(kernel_size, 0, kernel_size+1)
            x2d, y2d = np.meshgrid(x, y)

            #Make arrays that will work with the scipy optimise curve fit function
            x_y_coordinates = np.vstack((x2d.ravel(), y2d.ravel())) #turn the meshgrid into 2 rows of corresponding x and y coordinates
            correlation_1D = correlation.ravel() #convert correlation data into 1D

            # Use curve fit to fit correlation expression to the autocorelation. Occasionally this fails. So long as this doesn't happen to often its all good as Nans are ignored in further computation.
            try:
                auto_popt, auto_pcov = curve_fit(correlation_expression,x_y_coordinates,correlation_1D)
                c_part[xx,:] = abs(auto_popt[0:5]) #Amplitudes can be fit as negative and positive values, but we are only interested in the magnitude, hence taking the abs()
            except:
                c_part[xx,:] = np.nan
        return c_part
 
    # Check if save path is empty and create folder if it does not exist 
    if os.path.exists(SAVE_PATH):
        if any(os.scandir(SAVE_PATH)):
            val = input("Files already exist in current SAVE_PATH, do you want to continue? y/n: ")
            if val != 'y':
                return
    else:
        os.makedirs(SAVE_PATH)    

    # Read in images
    grid_image = tiff.imread(GRID_IMAGE_PATH)
    sample_and_grid_image = tiff.imread(SAMPLE_AND_GRID_IMAGE_PATH)
    image_height, image_width = np.shape(grid_image)  # Extract image width and height
    kernel_size_half = round(KERNEL_SIZE/2) # Determine half kernel size

    # create save data arrays
    sample_in_x = image_width-2*KERNEL_SIZE+1 #the number of data points in the x direction
    sample_in_y = image_height-2*KERNEL_SIZE+1 #the number of data points in the y direction
    c_gg = np.empty((sample_in_y,sample_in_x,5))
    c_gsg = np.empty((sample_in_y,sample_in_x,5))

    # Loop over each row in image
    if DASK:
        c_gg = [delayed(compute_coefficents)(grid_image[yy:yy+2*KERNEL_SIZE,:],grid_image[yy:yy+2*KERNEL_SIZE,:],sample_in_x,KERNEL_SIZE, kernel_size_half) for yy in range(sample_in_y)] #Loop over each row in grid-only image and compute auto-correlation coefficients 
        c_gsg = [delayed(compute_coefficents)(grid_image[yy:yy+2*KERNEL_SIZE,:],sample_and_grid_image[yy:yy+2*KERNEL_SIZE,:],sample_in_x, KERNEL_SIZE, kernel_size_half) for yy in range(sample_in_y)] #Loop over each row in grid-only and sample-and-grid image and compute cross-correlation coefficients
        
        with Profiler() as prof, ProgressBar():
            c_gg = compute(*c_gg, scheduler='processes')
            c_gsg = compute(*c_gsg, scheduler='processes')
        c_gg = np.array(c_gg)
        c_gsg = np.array(c_gsg)

    else:
        for yy in range(sample_in_y): #Loop over the image in the y direction
            c_gg[yy,:,:] = compute_coefficents(grid_image[yy:yy+2*KERNEL_SIZE,:],grid_image[yy:yy+2*KERNEL_SIZE,:],sample_in_x, KERNEL_SIZE, kernel_size_half)
            c_gsg[yy,:,:] = compute_coefficents(grid_image[yy:yy+2*KERNEL_SIZE,:],sample_and_grid_image[yy:yy+2*KERNEL_SIZE,:],sample_in_x, KERNEL_SIZE, kernel_size_half)
            
    tiff.imsave(SAVE_PATH+"\\c_gg0.tif",c_gg[:,:,0])
    tiff.imsave(SAVE_PATH+"\\c_gg1.tif",c_gg[:,:,1])
    tiff.imsave(SAVE_PATH+"\\c_gg2.tif",c_gg[:,:,2])
    tiff.imsave(SAVE_PATH+"\\c_gg3.tif",c_gg[:,:,3])
    tiff.imsave(SAVE_PATH+"\\c_gg4.tif",c_gg[:,:,4])

    tiff.imsave(SAVE_PATH+"\\c_gsg0.tif",c_gsg[:,:,0])
    tiff.imsave(SAVE_PATH+"\\c_gsg1.tif",c_gsg[:,:,1])
    tiff.imsave(SAVE_PATH+"\\c_gsg2.tif",c_gsg[:,:,2])
    tiff.imsave(SAVE_PATH+"\\c_gsg3.tif",c_gsg[:,:,3])
    tiff.imsave(SAVE_PATH+"\\c_gsg4.tif",c_gsg[:,:,4])

if __name__ == '__main__':    
    DASK = True
    #config.set(num_workers=8) #Set the number of workers allowed. Comment out if wanting full workers.

    PERIOD =  #grid period in units of pixels, can use value given by kernel_size.py code, eg 12.5816
    KERNEL_SIZE =  # Can use integer value of grid period, half the grid period, or the kernel size given by kernel_size.py code, eg 7

    GRID_IMAGE_PATH = "" # eg "Example_data\\Stage_2-flat_and_darking_data\\Grid.tif"
    SAMPLE_AND_GRID_IMAGE_PATH = "" # eg "Example_data\\Stage_2-flat_and_darking_data\\Sample+Grid.tif"
    SAVE_PATH = "" # Path to save coefficient images in, eg "Example_data\\Stage_4-extract_dark_field\\"
    coefficient_images(GRID_IMAGE_PATH,SAMPLE_AND_GRID_IMAGE_PATH,SAVE_PATH,PERIOD,KERNEL_SIZE,DASK)
