# Directional dark field (DiDaFi) by Michelle K Croughan

#### Hello and welcome to my repository. 
This code is open source and you are welcome to use it freely under the BSD-3-Clause License. Basically all I want is that if you use my code in a way that contributes to some research output I ask that you cite my publication associated with the release of this code:

DOI:

Bibtec entry:

Possible sentence you could use: "For the analysis of our data we employed/modified publicly avaliable code for the single-grid dark field retrival algorithm developed by Croughan et al. to retireve quantitaive dark field measures of our sample \cite{}."

#### Papers that cite this work:
1.
2.
3.

Thank you very much!

# DiDaFi Manual

## Stage 1 - Collecting data
In order to use this code you must have data to analyse. This code has been developed for single-grid imaging using a wire mesh absorption grid. We hypothisis that to will work on other types of absoption/phase grid and irregular reference patterns, however have not tested and tweaked the code for those types of grids.

Each data set must contain a grid-only image and a sample-and-grid image. The grid ideal should be in the exact sample position in both images. While this algorithm can work on data that is not flat-and-dark correct, we recommend doing this step. So also collected some flat and dark-current images.

If your sample is dose sensitive and the exposure time is very short, we recommend that you take many grid-only, flat, and dark images of that same exposure time and average them together. This way all the reference images have low noise and do not contribute to artifates in the final results.

An example data set is provided in https://github.com/Xray-grill/DiDaFi_MKCroughan/tree/master/Example_data/Stage_1-collecting_data. If you would like any of the data presenting in "<final paper name>" please contact me.

#### Image for the sample-and-grid, grid-only, dark-current and flat-field images.
<p align="middle">
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/e98102cf6f77e30aaf04b6601dff3f8d14cd00ad/Example_data/Stage_1-collecting_data/Sample+grid.png" alt="Sample-and-grid image of a lemon slice." width="400" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/1e64f9d9df2848931d3b2c55449b53c9f420590f/Example_data/Stage_1-collecting_data/Grid.png" alt="Grid-only image" width="400" /> 
</p>
<p align="middle">
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/1e64f9d9df2848931d3b2c55449b53c9f420590f/Example_data/Stage_1-collecting_data/Dark.png" alt="dark-current image." width="400" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/1e64f9d9df2848931d3b2c55449b53c9f420590f/Example_data/Stage_1-collecting_data/Flat.png" alt="Flat-field image" width="400" /> 
</p>



## Stage 2 - Flat and darking data
I have included a snippit of code that can be used to flat and dark your images titled **flat_and_dark.py** and is located at https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/186afba8ac77a56680a81b44fafaae134addb3d3/flat_and_dark.py

#### Flat and darked sample-and-grid and grid-only images
<p align="middle">
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/186afba8ac77a56680a81b44fafaae134addb3d3/Example_data/Stage_2-flat_and_darking_data/Sample+grid.png" alt="Sample-and-grid image of a lemon slice." width="400" />
  <img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/186afba8ac77a56680a81b44fafaae134addb3d3/Example_data/Stage_2-flat_and_darking_data/Grid.png" alt="Grid-only image" width="400" /> 
</p>

## Stage 3 - Determine kernel size
This is a recommended optional step one can use to determine the optimal kernel size to use for analyses. This assumes you have a regular grid pattern with the same grid period in both horizontal and vertical directions. Use the code **kernel_size.py**, it is located at https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/cf1c8e35420c260ff0335375f47fe485e37260c8/kernel_size.py.
This code gives the option to use DASK to run the code quickly, and is highly recommended. You can see the number of works to limit how much CPU it uses (without a limit I don't recommend using the computer for much while the code is running).

The premise of this code is determine the best kernel size, $k$, to use for further analysis. The $c_{gg,n}$ images are computed as the auto-correlation of local grid-only image regions, in an ideal world they should be the same value across the whole image. Thus, "best kernel size" is defined as the kernel size that produces minimal variations in the $c_{gg,n}$ images.

The code produces plots like the one below, the lower the visibility in the coefficient images that better. 
 
<img src="https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/cf1c8e35420c260ff0335375f47fe485e37260c8/Example_data/Stage_3-determine_kernel_size/Coefficient_visibility_w_ab13.png" alt="Visibility plot" width="400" /> 

For this grid I note that the period is $p = 12.5816$ as per the title, and that this is for when averaging the image of $13 \times 13$ pixel regions. Looking at the curves for visibility for each coefficient I can see that using value of $k$ around $7$ or $19$ will be best. Using a higher value of $k$ will give less sensitivity to smaller blurring features, so I opt for $k = 7$.

## Stage 4 - Extract the coefficient images
Use the code coefficient_images.py located <a href = "https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/90f97e4ffb879d71f008c78d0d02e65347f1a6d3/coefficient_images.py" target = "_self">Here</a>. This code takes the grid-only and sample-and-grid images and computes the correlation between small regions of each image. The out put of this code is 10 image, 1 for each coefficient $c_{gg,0}$, $c_{gsg,0}$, $c_{gg,1}$, $c_{gsg,1}$... ect. As the applying this part of the algorithm is very computationally expensive, I save this coefficient images and an interim step. That way, if I want to change how I compute the simultaneous equations or how I downsize the image, I do no need to recompute the coefficients images.

#### Auto-correlation images $c_{gg,0}$, ..., $c_{gg,4}$
<p align="middle">
  <img src="" alt="c_gg,0" width="100" />
  <img src="" alt="c_gg,1" width="100" />
  <img src="" alt="c_gg,2" width="100" />
  <img src="" alt="c_gg,3" width="100" />
  <img src="" alt="c_gg,4" width="100" />
</p>

#### Cross-correlation images $c_{gsg,0}$, ..., $c_{gsg,4}$
<p align="middle">
  <img src="" alt="c_gsg,0" width="100" />
  <img src="" alt="c_gsg,1" width="100" />
  <img src="" alt="c_gsg,2" width="100" />
  <img src="" alt="c_gsg,3" width="100" />
  <img src="" alt="c_gsg,4" width="100" />
</p>

