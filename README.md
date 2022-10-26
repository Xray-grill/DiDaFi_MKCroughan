# Directional dark field (DiDaFi) by Michelle K Croughan

Hello and welcome to my repository. This code is open source and you are welcome to use it freely under the BSD-3-Clause License. Basically all I want is that if you use my code in a way that contributes to some research output I ask that you cite my publication associated with the release of this code:

DOI:

Bibtec entry:

Possible sentence you could use: "For the analysis of our data we employed/modified publicly avaliable code for the single-grid dark field retrival algorithm developed by Croughen et al. to retireve quantitaive dark field measures of our sample \cite{}."

Thank you very much!

# DiDaFi Manual

## Stage 1 - Collecting data
In order to use this code you must have data to analyse. This code has been developed for single-grid imaging using a wire mesh absorption grid. We hypothisis that to will work on other types of absoption/phase grid and irregular reference patterns.

Each data set must contain a grid-only image and a sample-and-grid image. The grid ideal should be in the exact sample position in both images. While this algorithm can work on data that is not flat-and-dark correct, we recommend doing this step. So also collected some flat and dark-current images.

If your sample is dose sensitive and the exposure time is very short, we recommend that you take many grid-only, flat, and dark images of that same exposure time and average them together. This way all the reference images have low noise and do not contribute to artifates in the final results.

An example data set is provided in <>. If you would like any of the data presenting in "<final paper name>" please contact me.

![Sample-and-grid image of a lemon slice.](https://github.com/Xray-grill/DiDaFi_MKCroughan/blob/e98102cf6f77e30aaf04b6601dff3f8d14cd00ad/Example_data/Stage_1-collecting_data/Sample+grid.png =256x216)

## Stage 2 - Flat and darking data

I have included a 