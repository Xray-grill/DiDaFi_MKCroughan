# Directional dark field (DiDaFi) by Michelle K Croughan

#### Hello and welcome to my repository. 
This code is open source and you are welcome to use it freely under the BSD-3-Clause License. Basically all I want is that if you use my code in a way that contributes to some research output I ask that you cite my publication associated with the release of this code:

DOI:

Bibtec entry:

Possible sentence you could use: "For the analysis of our data we employed/modified publicly available code for the single-grid dark field retrieval algorithm developed by Croughan et al. to retrieve quantitative dark field measures of our sample \cite{}."

#### Papers that cite this work:
1. You could be the first!

Thank you very much!

# DiDaFi Manual

## Stage 1 - Collecting data
This code has been developed for single-grid imaging using a wire mesh absorption grid. I hypothesise that it will work on other types of absorption/phase grid and irregular reference patterns, however, I have not tested and tweaked the code for those types of grids.

Each data set must contain a grid-only image, $I_g$, and a sample-and-grid image, $I_{sg}$. The grid should be in the exact sample position in both images. While this algorithm can work on data that is not flat-and-dark corrected, we recommend doing this step as not doing so can affect relative visibility changes resulting on only qualitative results. So collect some flat and dark-current images.

If your sample is dose sensitive and the exposure time is very short, we recommend that you take many grid-only, flat, and dark-current images of that same exposure time and average them together. This way all the reference images have low noise and do not contribute to artifacts in the final results.

An example data set is provided <a href = "https://github.com/Xray-grill/DiDaFi_MKCroughan/tree/master/Example_data/Stage_1-collecting_data" target = "_self">here</a>. If you would like any of the data presenting in my please contact me, I am more than willing to assist.

#### Sample-and-grid, grid-only, dark-current and flat-field images.
<p align="middle">
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/e98102cf6f77e30aaf04b6601dff3f8d14cd00ad/Example_data/Stage_1-collecting_data/Sample+grid.png" alt="Sample-and-grid image of a lemon slice." width="400" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/1e64f9d9df2848931d3b2c55449b53c9f420590f/Example_data/Stage_1-collecting_data/Grid.png" alt="Grid-only image" width="400" /> 
</p>
<p align="middle">
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/1e64f9d9df2848931d3b2c55449b53c9f420590f/Example_data/Stage_1-collecting_data/Dark.png" alt="dark-current image." width="400" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/1e64f9d9df2848931d3b2c55449b53c9f420590f/Example_data/Stage_1-collecting_data/Flat.png" alt="Flat-field image" width="400" /> 
</p>

## Stage 2 - Flat and darking data
I have included a snippet of code that can be used to flat and dark your images titled **flat_and_dark.py** and is located <a href = "https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/186afba8ac77a56680a81b44fafaae134addb3d3/flat_and_dark.py" target = "_self">here</a>.

#### Flat and darked sample-and-grid and grid-only images
<p align="middle">
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/186afba8ac77a56680a81b44fafaae134addb3d3/Example_data/Stage_2-flat_and_darking_data/Sample+grid.png" alt="Sample-and-grid image of a lemon slice." width="400" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/186afba8ac77a56680a81b44fafaae134addb3d3/Example_data/Stage_2-flat_and_darking_data/Grid.png" alt="Grid-only image" width="400" /> 
</p>

## Stage 3 - Determine kernel size
This is a recommended optional step one can use to determine the optimal kernel size to use for analyses. This assumes you have a regular grid pattern with the same grid period in both horizontal and vertical directions. Use the code **kernel_size.py**, it is located <a href = "https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/cf1c8e35420c260ff0335375f47fe485e37260c8/kernel_size.py" target = "_self">here</a>.
This code gives the option to use DASK to run the code quickly, and is highly recommended. You can set the number of workers to limit how much CPU it uses (without a limit I don't recommend using the computer for much while the code is running).

The premise of this code is determine the best kernel size, $k$, to use for further analysis. The $c_{gg,n}$ images are computed as the auto-correlation of local grid-only image regions, in an ideal world they should be the same value across the whole image. Thus, "best kernel size" is defined as the kernel size that produces the lowest visibility in the $c_{gg,n}$ images.

The code produces plots like the one below, the lower the visibility in the coefficient images that better. 
 
<img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/cf1c8e35420c260ff0335375f47fe485e37260c8/Example_data/Stage_3-determine_kernel_size/Coefficient_visibility_w_ab13.png" alt="Visibility plot" width="400" /> 

For this grid I note that the period is $p = 12.5816$ as per the title, and that this is for when averaging the image of $13 \times 13$ pixel regions. Looking at the curves for visibility for each coefficient I can see that using value of $k$ around $7$ or $19$ will be best. Using a higher value of $k$ will give less sensitivity to smaller blurring features, so I opt for $k = 7$.

## Stage 4 - Extract the coefficient images
Use the code **coefficient_images.py** located <a href = "https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/90f97e4ffb879d71f008c78d0d02e65347f1a6d3/coefficient_images.py" target = "_self">here</a>. This code takes the grid-only and sample-and-grid images and computes the correlation between small regions of each image. The output of this code is ten images, one for each coefficient $c_{gg,0}$, $c_{gsg,0}$, $c_{gg,1}$, $c_{gsg,1}$... ect. As applying this part of the algorithm is very computationally expensive, I save these coefficient images as an interim step. That way, if I want to change how I compute the simultaneous equations or how I downsize the image, I do not need to recompute the coefficients images.

#### Auto-correlation images $c_{gg,0}$, ..., $c_{gg,4}$
<p align="middle">
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/907fc933961ceb0c7b16c78266559a4448f6ddea/Example_data/Stage_4-dark_field_retrieval/c_gg0.png" alt="c_gg,0" width="100" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/907fc933961ceb0c7b16c78266559a4448f6ddea/Example_data/Stage_4-dark_field_retrieval/c_gg1.png" alt="c_gg,1" width="100" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/907fc933961ceb0c7b16c78266559a4448f6ddea/Example_data/Stage_4-dark_field_retrieval/c_gg2.png" alt="c_gg,2" width="100" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/907fc933961ceb0c7b16c78266559a4448f6ddea/Example_data/Stage_4-dark_field_retrieval/c_gg3.png" alt="c_gg,3" width="100" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/907fc933961ceb0c7b16c78266559a4448f6ddea/Example_data/Stage_4-dark_field_retrieval/c_gg4.png" alt="c_gg,4" width="100" />
</p>

#### Cross-correlation images $c_{gsg,0}$, ..., $c_{gsg,4}$
<p align="middle">
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/907fc933961ceb0c7b16c78266559a4448f6ddea/Example_data/Stage_4-dark_field_retrieval/c_gsg0.png" alt="c_gsg,0" width="100" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/907fc933961ceb0c7b16c78266559a4448f6ddea/Example_data/Stage_4-dark_field_retrieval/c_gsg1.png" alt="c_gsg,1" width="100" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/907fc933961ceb0c7b16c78266559a4448f6ddea/Example_data/Stage_4-dark_field_retrieval/c_gsg2.png" alt="c_gsg,2" width="100" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/907fc933961ceb0c7b16c78266559a4448f6ddea/Example_data/Stage_4-dark_field_retrieval/c_gsg3.png" alt="c_gsg,3" width="100" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/907fc933961ceb0c7b16c78266559a4448f6ddea/Example_data/Stage_4-dark_field_retrieval/c_gsg4.png" alt="c_gsg,4" width="100" />
</p>

## Stage 5 - Retrieve directional dark field parameters and metrics
This step produces all the fun images with information about the directional dark field of the sample! Use the dark_field_retrieval.py code found <a href = "https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/a130e778aaa576a829f5e7a4ec08ff87c800c6f0/dark_field_retrieval.py" target = "_self">here</a>. First the coefficient images are downsized by a factor of the grid period. This removes as much of the oscillations due to having a non-integer grid period as possible (as you can see above the results from the correlations depend on what part of the grid is included in the kernel). Then it uses the new coefficient image to determine the dark field parameters, $\theta$, $\T$, $\sigma_M$ and $\sigma_m$. Using these parameters it computes the dark field scattering angles $\Theta_M$ and $\Theta_m$ and final the metrics for strength, $\Theta_{RMS}$ and asymmetry, $\Theta_{ASY}$.

#### Major scattering angle $\Theta_M$, minor scattering angle $\Theta_m$, and sample transmission $T$
<p align="middle">
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/a130e778aaa576a829f5e7a4ec08ff87c800c6f0/Example_data/Stage_5-dark_field_retrieval/Theta_major.png" alt="Major" width="200" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/a130e778aaa576a829f5e7a4ec08ff87c800c6f0/Example_data/Stage_5-dark_field_retrieval/Theta_minor.png" alt="Minor" width="200" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/a130e778aaa576a829f5e7a4ec08ff87c800c6f0/Example_data/Stage_5-dark_field_retrieval/sample_transmission.png" alt="transmission" width="200" />
</p>

#### RMS scattering angle $\Theta_{RMS}$, asymmetry $\Theta_{ASY}$, and directional angle $\theta$
<p align="middle">
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/a130e778aaa576a829f5e7a4ec08ff87c800c6f0/Example_data/Stage_5-dark_field_retrieval/strength.png" alt="RMS" width="200" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/a130e778aaa576a829f5e7a4ec08ff87c800c6f0/Example_data/Stage_5-dark_field_retrieval/asymmetry.png" alt="ASY" width="200" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/a130e778aaa576a829f5e7a4ec08ff87c800c6f0/Example_data/Stage_5-dark_field_retrieval/theta.png" alt="theta" width="200" />
</p>

## Stage 6 - Create HSV image
The final code help visualise the data is called **hsv_image.py** and can be found <a href = "https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/a130e778aaa576a829f5e7a4ec08ff87c800c6f0/hsv_image.py" target = "_self">here</a>. Hue, saturation, value (HSV) images are a really neat way to combine 3 different "gray" images. Each component of the HSV image ranges from $0$ to $1$. For my work I have selected the following
* Hue - The colour of the image represents the value of $\theta$, the dominant scattering direction. $0$ gives a red colour, and then as it increases it goes through the rainbow (orange, yellow, green ect) back to red when it reaches $1$. Thus we map the scatter that is bound between $0$ and $\pi$ radians to $0$ and $1$. This give vertical scattering a red colour, and horizontal scattering a light blue colour.
* Saturation - This describes how "colourful" the pixel is. At $0$ the pixel will appear white/grey/black (depending on the value) and at $1$ the pixel will be in full colour. I map the scattering asymmetry, $\Theta_{RMS}$, to saturation, so isometric scattering (low asymmetry) does not show in colour and thus hides the irrelevant hue of the pixel.
* Value - This is mapped to the strength of the scattering, $\Theta_{RMS}$, and determines how bright the pixel appears. The strength is scaled to be between $0$ and $1$, where any complex values are mapped to $0$ and the maximum strength in the image is mapped to $1$. Sometimes if there is a pixel or small region that has a very high strength, you might want to map the max$\times 0.8$, or something like $2\sigma$, where $\sigma$ is the standard deviation of the strength values in the image.
Combining all these produces an image of the sample that is much easier to interpret than the individual images in the previous step.

#### HSV image

<img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/907fc933961ceb0c7b16c78266559a4448f6ddea/Example_data/Stage_6-HSV_image/HSV_image.png" alt="HSV image" width="400" /> 
