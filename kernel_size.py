#Code written by Michelle K Croughan, Monash University Australia, 2022
#This code and license can be found at https://github.com/Xray-grill/DiDaFi_MKCroughan
#Any research output utilising this code must reference this published article: <DOI of article>

import tifffile as tiff
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import correlate
from math import floor, ceil
from dask import delayed, compute, config
from dask.diagnostics import Profiler, ProgressBar

def find_kernel_size(GRID_IMAGE,SAVE_PATH,DASK,MAX_PERIOD):

    def extract_period(image): # Take fourier transform of grid image to determine estimate of period.
        height,width = np.shape(image) # Extract height and shape of image

        all_periods_in_x = 1/abs(np.fft.fftfreq(width, 1)) # Array with the spatial periods (1/frequency) along the x-axis in fourier space, in units of pixels
        all_periods_in_y = 1/abs(np.fft.fftfreq(height, 1)) # Array with the spatial periods (1/frequency) along the y-axis in fourier space, in units of pixels
        possible_periods_in_x = all_periods_in_x[all_periods_in_x < MAX_PERIOD] # Reduce array to only include possible periods
        possible_periods_in_y = all_periods_in_y[all_periods_in_y < MAX_PERIOD] # Reduce array to only include possible periods

        grid_fft = abs(np.fft.fft2(image)) #take fourier transform of image and take the absolute value of these
        grid_fft_x = np.sum(grid_fft,axis=0) #sum the fourier transform along the x axis
        grid_fft_x = grid_fft_x[all_periods_in_x < MAX_PERIOD] #Trim the out spatial periods that are larger than MAX_PERIOD
        grid_fft_y = np.sum(grid_fft,axis=1) #sum the fourier transform along the y axis
        grid_fft_y = grid_fft_y[all_periods_in_y < MAX_PERIOD] #Trim the out spatial periods that are larger than MAX_PERIOD

        guess_period_x = possible_periods_in_x[np.argmax(grid_fft_x)] #Find the frequency with the largest magnitude in x, and use this to extract the associated period
        guess_period_y = possible_periods_in_y[np.argmax(grid_fft_y)] #Find the frequency with the largest magnitude in x, and use this to extract the associated period

        return np.mean((guess_period_x,guess_period_y)) #take the average of the two period estimates

    def correlation_expression(x_y_coordinates,c_0,c_1,c_2,c_3,c_4,phase_1,phase_2):
        # Define function to fit to autocorrelation of I_g and crosscorrelation of I_g and I_sg. Allow phase of trig functions to be a free parameter.
        x2d, y2d = x_y_coordinates
        return c_0 + c_1*np.cos((2. *np.pi *x2d)/grid_period +phase_1)+ \
            c_2*np.cos((2.*np.pi *y2d)/grid_period +phase_2)+ \
            c_3*np.cos((2. *np.pi *(x2d-y2d))/grid_period +phase_1-phase_2)+ \
            c_4*np.cos((2. *np.pi *(x2d+y2d))/grid_period + phase_1+phase_2)

    def compute_coefficents(row,sample_in_x, kernel_size, kernel_size_half):
        c_gg_part = np.empty((sample_in_x,5)) # Create array to store the row data in
        for xx in range(sample_in_x):
            # Pull out sub arrays needed to perform correlations
            kernel = row[kernel_size_half:kernel_size_half+kernel_size,xx+kernel_size_half:xx+kernel_size_half+kernel_size] # k by k region
            window = row[:,xx:xx+2*kernel_size] # 2k by 2k region. 

            autocorrelation = correlate(window,kernel,mode = 'valid')
            
            #Make 2d meshgrid the size of the subarrays in autocorrelation space
            x = np.linspace(0, kernel_size,kernel_size+1)
            y = np.linspace(kernel_size, 0, kernel_size+1)
            x2d, y2d = np.meshgrid(x, y)

            #Make arrays that will work with the scipy optimise curve fit function
            x_y_coordinates = np.vstack((x2d.ravel(), y2d.ravel())) #turn the meshgrid into 2 rows of corresponding x and y coordinates
            autocorrelation_1D = autocorrelation.ravel() #convert autocorrelation data into 1D array

            # Use curve fit to fit correlation expression to the autocorrelation. Occasionally this fails. So long as this doesn't happen to often its all good as Nans are ignored in further computation.
            try:
                auto_popt, auto_pcov = curve_fit(correlation_expression,x_y_coordinates,autocorrelation_1D)
                c_gg_part[xx,:] = abs(auto_popt[0:5])
            except:
                c_gg_part[xx,:] = np.nan
                print(" Unable to fit ", (kernel_size, xx))

        return c_gg_part
    
    grid_period = extract_period(GRID_IMAGE) # Determine the grid period, p.
    kernel_sizes = np.array(range(round(grid_period/2),round(grid_period*2))) # Create an array of kernel sizes, k, to investigate. 
    average_bys = np.array([floor(grid_period),ceil(grid_period)]) # Create an array of average by factors that are integer values either side of the grid period.
    
    #Crop down the grid image to reduce run time of code.
    region_size = max(kernel_sizes)*15 # Compute region size that is big enough for at least 15 times the size of the largest kernel.
    half_height, half_width = int(np.shape(GRID_IMAGE)[0]/2), int(np.shape(GRID_IMAGE)[1]/2) # Find the coordinates for the centre pixel of the image
    half_region = int(region_size/2)
    grid_image = GRID_IMAGE[half_height-half_region:half_height+half_region,half_width-half_region:half_width+half_region] #Crop the image down to reduce processing time.
    image_height,image_width = np.shape(grid_image)    

    visibility = np.zeros((len(kernel_sizes),len(average_bys),5)) # Array to store visibility for each c_gg,n term at each kernel size and averaging factor

    for k, kernel_size in enumerate(kernel_sizes): # Loop over each kernel size
        kernel_size_half = int(kernel_size/2)

        sample_in_x = image_width-2*kernel_size+1 #the number of data points in the x direction
        sample_in_y = image_height-2*kernel_size+1 #the number of data points in the y direction

        c_gg = np.empty((sample_in_y,sample_in_x,5)) # create save data array for the c_gg,n coefficients
        print("Processing kernel size {}. Max kernel size to investigate is {}".format(kernel_size, np.max(kernel_size)))

        if DASK: # If using DASK process using this method
            values = [delayed(compute_coefficents)(grid_image[yy:yy+2*kernel_size,:],sample_in_x, kernel_size, kernel_size_half) for yy in range(sample_in_y)] # Loop over each row in the image, giving each row to a worker.
            with Profiler() as prof, ProgressBar(): #
                c_gg = compute(*values, scheduler='processes')
            c_gg = np.array(c_gg)
        else:
            for yy in range(sample_in_y): #Loop over each row in the image
                c_gg[yy,:,:] = compute_coefficents(grid_image[yy:yy+2*kernel_size,:],sample_in_x, kernel_size, kernel_size_half) # Compute the cooefficents for each column in the row.
                
        for a, average_by in enumerate(average_bys): # Loop over each average by to see which works best with this kernel size.
            #Determine how many rounded grid-periods fit into coefficient images
            periods_in_x = c_gg[:,:,3].shape[1]//average_by
            periods_in_y = c_gg[:,:,3].shape[0]//average_by

            #Use reshape to easily average each p x p region of the image, ignoring nans
            c0 = np.nanmean(c_gg[0:average_by*periods_in_y,0:average_by*periods_in_x,0].reshape(periods_in_y,average_by,periods_in_x,average_by), axis=(1,3))
            c1 = np.nanmean(c_gg[0:average_by*periods_in_y,0:average_by*periods_in_x,1].reshape(periods_in_y,average_by,periods_in_x,average_by), axis=(1,3))
            c2 = np.nanmean(c_gg[0:average_by*periods_in_y,0:average_by*periods_in_x,2].reshape(periods_in_y,average_by,periods_in_x,average_by), axis=(1,3))
            c3 = np.nanmean(c_gg[0:average_by*periods_in_y,0:average_by*periods_in_x,3].reshape(periods_in_y,average_by,periods_in_x,average_by), axis=(1,3))
            c4 = np.nanmean(c_gg[0:average_by*periods_in_y,0:average_by*periods_in_x,4].reshape(periods_in_y,average_by,periods_in_x,average_by), axis=(1,3))

            # Compute visibility of each coefficient.
            c0_visibility = (np.nanmax(c0) - np.nanmin(c0)) / (np.nanmax(c0) + np.nanmin(c0))
            c1_visibility = (np.nanmax(c1) - np.nanmin(c1)) / (np.nanmax(c1) + np.nanmin(c1))
            c2_visibility = (np.nanmax(c2) - np.nanmin(c2)) / (np.nanmax(c2) + np.nanmin(c2))
            c3_visibility = (np.nanmax(c3) - np.nanmin(c3)) / (np.nanmax(c3) + np.nanmin(c3))
            c4_visibility = (np.nanmax(c4) - np.nanmin(c4)) / (np.nanmax(c4) + np.nanmin(c4))

            # Store the results
            visibility[k,a,:] = np.array((c0_visibility,c1_visibility,c2_visibility,c3_visibility,c4_visibility))
    
    # Create plots        
    for a, average_by in enumerate(average_bys):
        for c in range(0,5):
            plt.plot(kernel_sizes, visibility[:,a,c], label = "c_gg,{}".format(c))
        plt.xlabel("Kernel size (pixles)")
        plt.ylabel("Visibility of coefficients")
        plt.legend()
        plt.title("Grid period = {}, Average by = {}".format(grid_period, average_by))
        plt.savefig(SAVE_PATH+"Coefficient_visibility_w_ab{}".format(average_by))
        plt.show()
        plt.clf()

if __name__ == '__main__':
    GRID_IMAGE= tiff.imread("") # Read in the grid-only image 
    SAVE_FOLDER = "" #Remember to make folder, saves plots in here.
    MAX_PERIOD =  #Maximum period that we would responsibly expect a grid to have in pixels

    DASK = True # Set to True to use DASK
    #config.set(num_workers=8) #Set the number of workers allowed. Comment out if wanting full workers.

    find_kernel_size(GRID_IMAGE,SAVE_FOLDER,DASK,MAX_PERIOD)
    


