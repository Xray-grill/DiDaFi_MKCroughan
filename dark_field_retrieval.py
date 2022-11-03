import tifffile as tiff
import numpy as np
import os

def retrieve_dark_field(PATH,SAVE_PATH,PERIOD,AVERAGE_BY,ODD,PIXEL_SIZE):
    def simultaneous_equations(ratio0,ratio1,ratio2,ratio3,ratio4):
        sample_transmission = ratio0

        a1 = PERIOD**2/np.pi**2 * np.log(ratio1/sample_transmission)
        a2 = PERIOD**2/np.pi**2 * np.log(ratio2/sample_transmission)
        a3 = PERIOD**2/(2.*np.pi**2) * np.log(ratio3/sample_transmission)
        a4 = PERIOD**2/(2.*np.pi**2) * np.log(ratio4/sample_transmission)

        theta = 0.5 * np.arctan2((a4-a3),(a2-a1)) # np.arctan2 function is used to ensure correct angle is chosen. 

        #Compute sigma_x and sigma_y using the least squares method. Add +0j to make array complex data type
        sigma_x_squared = 1./8.*(-a1*(2.*np.cos(2.*theta)+1.) +a2*(2*np.cos(2.*theta)-1)-a3*(2.*np.sin(2.*theta)+1) +a4*(2.*np.sin(2.*theta)-1)) +0j
        sigma_y_squared = 1./8.*( a1*(2.*np.cos(2.*theta)-1.) -a2*(2*np.cos(2.*theta)+1)+a3*(2.*np.sin(2.*theta)-1) -a4*(2.*np.sin(2.*theta)+1)) +0j
        sigma_x = np.sqrt(sigma_x_squared)
        sigma_y = np.sqrt(sigma_y_squared)

        return sample_transmission, theta, sigma_x, sigma_y, sigma_x_squared, sigma_y_squared

    def update_coordinate_space(th,sig_x, sig_y, sig_x_sq, sig_y_sq):
        semi_maj = sig_y.copy() 
        semi_maj[sig_y_sq < sig_x_sq] = sig_x[sig_y_sq < sig_x_sq] # set to be the larger blurring width

        semi_min = sig_x.copy()
        semi_min[sig_y_sq < sig_x_sq] = sig_y[sig_y_sq < sig_x_sq] # set to be the smaller blurring width

        th[sig_y_sq < sig_x_sq] += np.pi/2 

        th[th<0] += np.pi 
        th[th>np.pi] -= np.pi 

        return th, semi_maj, semi_min

    def compute_df_metrics(semi_maj,semi_min):
        strength = np.sqrt((semi_min**2+semi_maj**2)/2)

        # Piecewise function for asymmetry
        asymmetry = 1 - semi_min/semi_maj
        asymmetry[(asymmetry > 2/3) | (np.iscomplex(asymmetry))] = np.sqrt((semi_maj[asymmetry > 2/3]**2-semi_min[asymmetry > 2/3]**2)/(2*semi_maj[asymmetry > 2/3]**2))
        asymmetry[np.iscomplex(strength)]=0
        return asymmetry, strength

    def make_real_image(complex_array): 
        #convert complex array into image where complex values are converted to negative real values.
        real_array = complex_array.copy() 
        real_array[np.iscomplex(complex_array)] = - np.abs(complex_array[np.iscomplex(complex_array)]) # make the complex parts negative real
        real_array = real_array.real # remove the complex part from the array so dtype is float.
        return real_array

    # Check if save path is empty and create folder if it does not exist 
    if os.path.exists(SAVE_PATH):
        if any(os.scandir(SAVE_PATH)):
            val = input("Files already exist in current SAVE_PATH, do you want to continue? y/n: ")
            if val != 'y':
                return #move onto next data set
    else:
        os.makedirs(SAVE_PATH)    

    ### Read in coefficient images ###
    c_gg0 = tiff.imread(PATH+"c_gg0.tif")
    c_gg1 = tiff.imread(PATH+"c_gg1.tif")
    c_gg2 = tiff.imread(PATH+"c_gg2.tif")
    c_gg3 = tiff.imread(PATH+"c_gg3.tif")
    c_gg4 = tiff.imread(PATH+"c_gg4.tif")
    c_gsg0 = tiff.imread(PATH+"c_gsg0.tif")
    c_gsg1 = tiff.imread(PATH+"c_gsg1.tif")
    c_gsg2 = tiff.imread(PATH+"c_gsg2.tif")
    c_gsg3 = tiff.imread(PATH+"c_gsg3.tif")
    c_gsg4 = tiff.imread(PATH+"c_gsg4.tif")

    # Average grid period regions of the coefficients images. 
    periods_in_x = c_gg0.shape[1]//AVERAGE_BY
    periods_in_y = c_gg0.shape[0]//AVERAGE_BY

    c_gg0 = np.nanmean(c_gg0[0:AVERAGE_BY*periods_in_y,0:AVERAGE_BY*periods_in_x].reshape(periods_in_y,AVERAGE_BY,periods_in_x,AVERAGE_BY),axis=(3,1))
    c_gg1 = np.nanmean(c_gg1[0:AVERAGE_BY*periods_in_y,0:AVERAGE_BY*periods_in_x].reshape(periods_in_y,AVERAGE_BY,periods_in_x,AVERAGE_BY),axis=(3,1))
    c_gg2 = np.nanmean(c_gg2[0:AVERAGE_BY*periods_in_y,0:AVERAGE_BY*periods_in_x].reshape(periods_in_y,AVERAGE_BY,periods_in_x,AVERAGE_BY),axis=(3,1))
    c_gg3 = np.nanmean(c_gg3[0:AVERAGE_BY*periods_in_y,0:AVERAGE_BY*periods_in_x].reshape(periods_in_y,AVERAGE_BY,periods_in_x,AVERAGE_BY),axis=(3,1))
    c_gg4 = np.nanmean(c_gg4[0:AVERAGE_BY*periods_in_y,0:AVERAGE_BY*periods_in_x].reshape(periods_in_y,AVERAGE_BY,periods_in_x,AVERAGE_BY),axis=(3,1))
    c_gsg0 = np.nanmean(c_gsg0[0:AVERAGE_BY*periods_in_y,0:AVERAGE_BY*periods_in_x].reshape(periods_in_y,AVERAGE_BY,periods_in_x,AVERAGE_BY),axis=(3,1))
    c_gsg1 = np.nanmean(c_gsg1[0:AVERAGE_BY*periods_in_y,0:AVERAGE_BY*periods_in_x].reshape(periods_in_y,AVERAGE_BY,periods_in_x,AVERAGE_BY),axis=(3,1))
    c_gsg2 = np.nanmean(c_gsg2[0:AVERAGE_BY*periods_in_y,0:AVERAGE_BY*periods_in_x].reshape(periods_in_y,AVERAGE_BY,periods_in_x,AVERAGE_BY),axis=(3,1))
    c_gsg3 = np.nanmean(c_gsg3[0:AVERAGE_BY*periods_in_y,0:AVERAGE_BY*periods_in_x].reshape(periods_in_y,AVERAGE_BY,periods_in_x,AVERAGE_BY),axis=(3,1))
    c_gsg4 = np.nanmean(c_gsg4[0:AVERAGE_BY*periods_in_y,0:AVERAGE_BY*periods_in_x].reshape(periods_in_y,AVERAGE_BY,periods_in_x,AVERAGE_BY),axis=(3,1))

    sample_transmission, theta, sigma_x, sigma_y, sigma_x_squared, sigma_y_squared = simultaneous_equations(c_gsg0/c_gg0,c_gsg1/c_gg1,c_gsg2/c_gg2,c_gsg3/c_gg3,c_gsg4/c_gg4)

    # Compute major and minor blurring width and adjust theta 
    theta, sigma_major, sigma_minor = update_coordinate_space(theta.copy(),sigma_x,sigma_y,sigma_x_squared,sigma_y_squared)

    #compute the scattering cone half-angles using the small angle approximation.
    Theta_major = (sigma_major*PIXEL_SIZE)/ODD
    Theta_minor = (sigma_minor*PIXEL_SIZE)/ODD

    #compute strength and asymmetry
    asymmetry, strength = compute_df_metrics(Theta_major,Theta_minor)

    tiff.imsave(SAVE_PATH+"\\theta.tif",theta)
    tiff.imsave(SAVE_PATH+"\\sigma_major.tif",make_real_image(sigma_major))
    tiff.imsave(SAVE_PATH+"\\sigma_minor.tif",make_real_image(sigma_minor))
    tiff.imsave(SAVE_PATH+"\\sample_transmission.tif",sample_transmission)
    tiff.imsave(SAVE_PATH+"\\strength.tif",make_real_image(strength))
    tiff.imsave(SAVE_PATH+"\\asymmetry.tif",make_real_image(asymmetry))
    tiff.imsave(SAVE_PATH+"\\Theta_major.tif",make_real_image(Theta_major))
    tiff.imsave(SAVE_PATH+"\\Theta_minor.tif",make_real_image(Theta_minor))

if __name__ == '__main__':
    PERIOD = # eg12.5816
    AVERAGE_BY = #Rounded value of the grid period, either up or down. eg 13
    ODD =  #object to detector distance in meters. eg 1.5
    PIXEL_SIZE =  #pixel size in units of meters. 1um = 1e-6m, eg 12.3e-6
    COEFFICIENT_PATH = "" # eg "Example_data\\Stage_4-coefficient_images\\"
    SAVE_PATH = "" # eg "Example_data\\Stage_5-dark_field_retrieval\\"
    retrieve_dark_field(COEFFICIENT_PATH,SAVE_PATH,PERIOD,AVERAGE_BY,ODD,PIXEL_SIZE)







    





