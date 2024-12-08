# Bad Pixels locations and adding bad pixels to an image

import os
import numpy as np
from prose import FitsManager, FITSImage, Telescope
from astropy.io import fits

def bad_pixel_locations(
        image, 
        hot_percentage, 
        dead_percentage, 
        hot_peak, 
        hot_std_dev, 
        hot_upper_limit, 
        dead_mean=0, 
        dead_std_dev=10, 
        dead_lower_limit=0):
    """
    Generate the locations and values of hot and dead pixels in an image.

    Parameters:
        image (np.ndarray): Input 2D image array.
        hot_percentage (float): Percentage of pixels to set as hot pixels.
        dead_percentage (float): Percentage of pixels to set as dead pixels.
        hot_peak (float): Mean value for the Gaussian distribution of hot pixels.
        hot_std_dev (float): Standard deviation for the Gaussian distribution of hot pixels.
        hot_lower_limit (float): Minimum value for the hot pixels.
        hot_upper_limit (float): Maximum value for the hot pixels.
        dead_mean (float): Mean value for the Gaussian distribution of dead pixels.
        dead_std_dev (float): Standard deviation for the Gaussian distribution of dead pixels.
        dead_lower_limit (float): Minimum value for the dead pixels.
        dead_upper_limit (float): Maximum value for the dead pixels.

    Returns:
        np.ndarray: Indices and values of the hot and cold pixels.
    """

    # Copy the image to avoid modifying the original
    modified_image = np.copy(image)

    # Calculate the total number of pixels to set as hot and dead
    total_pixels = modified_image.size
    num_hot_pixels = int(total_pixels * (hot_percentage / 100))
    num_dead_pixels = int(total_pixels * (dead_percentage / 100))

    # Randomly select unique indices for hot and dead pixels
    hot_indices = np.random.choice(total_pixels, num_hot_pixels, replace=False)
    remaining_indices = np.setdiff1d(np.arange(total_pixels), hot_indices)
    dead_indices = np.random.choice(remaining_indices, num_dead_pixels, replace=False)

    # Convert indices to the original shape
    hot_indices = np.unravel_index(hot_indices, modified_image.shape)
    dead_indices = np.unravel_index(dead_indices, modified_image.shape)

    # Generate hot pixel values from a Gaussian distribution, clipped to the specified range
    hot_pixel_values = []
    while len(hot_pixel_values) < num_hot_pixels:
        sample = np.random.normal(loc=hot_peak, scale=np.sqrt(hot_std_dev))
        if sample <= hot_upper_limit:
            hot_pixel_values.append(sample)
    hot_pixel_values = np.array(hot_pixel_values)

    # Generate dead pixel values from a Gaussian distribution within the [dead_lower_limit, dead_upper_limit]
    dead_pixel_values = []
    while len(dead_pixel_values) < num_dead_pixels:
        sample = np.random.normal(loc=dead_mean, scale=dead_std_dev)
        if dead_lower_limit <= sample:
            dead_pixel_values.append(sample)
    dead_pixel_values = np.array(dead_pixel_values)
    
    return hot_indices, dead_indices, hot_pixel_values, dead_pixel_values

def add_bad_pixels(dir_raw_images, dir_bad_images, hot_indices, dead_indices, hot_pixel_values, dead_pixel_values):
    """
    Introduce hot and dead pixels into an image while ensuring no overlap in indices and setting value limits for both types of pixels.
    
    Parameters:
        dir_raw_images (str): Directory containing the raw images.
        dir_bad_images (str): Directory to save the images with bad pixels.
        hot_indices (tuple): Indices of the hot pixels.
        dead_indices (tuple): Indices of the dead pixels.
        hot_pixel_values (np.ndarray): Values for the hot pixels.
        dead_pixel_values (np.ndarray): Values for the dead pixels.

    Returns:
        np.ndarray: Saves the images with bad pixels in the specified directory.
    """

    fm = FitsManager(dir_raw_images, depth=1)

    dir_bad_images = "./images_all_guiding_hot_cold_warm_pixels"
    os.makedirs(dir_bad_images, exist_ok=True)

    for i in range(len(fm.all_images)):
        raw_image = FITSImage(fm.all_images[i]).data  # 1024x1024 image filled with ones

        # Set hot pixel values
        raw_image[hot_indices] = hot_pixel_values
        # Set dead pixel values
        raw_image[dead_indices] = dead_pixel_values   

        raw_output_filename = os.path.join(dir_bad_images, f"image_light_hcw_pixels_{i+1}.fits")

        # Save the raw image in "images_generated" directory
        fits.writeto(raw_output_filename, raw_image, overwrite=True, header=fits.Header([
            (Telescope.keyword_image_type, Telescope.keyword_light_images),
            (Telescope.keyword_observation_date, FITSImage(fm.all_images[i]).date.strftime('%Y-%m-%dT%H:%M:%S.%f'))
        ]))
    
    for i in range(len(fm.all_darks)):
        raw_image = FITSImage(fm.all_darks[i]).data  # 1024x1024 image filled with ones

        # Set hot pixel values
        raw_image[hot_indices] = hot_pixel_values
        # Set dead pixel values
        raw_image[dead_indices] = dead_pixel_values   

        raw_output_filename = os.path.join(dir_bad_images, f"image_dark_hcw_pixels_{i+1}.fits")

        # Save the raw image in "images_generated" directory
        fits.writeto(raw_output_filename, raw_image, overwrite=True, header=fits.Header([
            (Telescope.keyword_image_type, Telescope.keyword_dark_images),
            (Telescope.keyword_observation_date, FITSImage(fm.all_darks[i]).date.strftime('%Y-%m-%dT%H:%M:%S.%f'))
        ]))

    print(f"Light and dark images with bad pixels have been modified and saved in {dir_bad_images}")

def add_telegraphic_pixels(dir_raw_images, dir_bad_images, telegraphic_percentage, interval, telegraphic_pixel_values=0):
    """
    Introduce telegraphic pixels into an image while ensuring no overlap in indices and setting value limits for telegraphic pixels.
    
    Parameters:
        dir_raw_images (str): Directory containing the raw images.
        dir_bad_images (str): Directory to save the images with telegraphic pixels.
        telegraphic_indices (tuple): Indices of the telegraphic pixels.
        telegraphic_pixel_values (np.ndarray): Values for the telegraphic pixels.

    Returns:
        np.ndarray: Saves the images with telegraphic pixels in the specified directory.
    """

    fm = FitsManager(dir_raw_images, depth=1)
    modified_image = FITSImage(fm.all_images[0]).data  # 1024x1024 image filled with ones
    
    dir_bad_images = "./images_all_guiding_bad_pixels"
    os.makedirs(dir_bad_images, exist_ok=True)

    total_pixels = modified_image.size
    num_telegraphic_pixels = int(total_pixels * (telegraphic_percentage / 100))
    telegraphic_indices = np.random.choice(total_pixels, num_telegraphic_pixels, replace=False)
    telegraphic_indices = np.unravel_index(telegraphic_indices, modified_image.shape)

    for i in range(len(fm.all_images)):
    
        raw_image = FITSImage(fm.all_images[i]).data  # 1024x1024 image filled with ones
        
        if i%interval == 0 and i != 0:
            # Set hot pixel values
            raw_image[telegraphic_indices] = telegraphic_pixel_values
            # Set dead pixel values
            raw_image[telegraphic_indices] = telegraphic_pixel_values   

        raw_output_filename = os.path.join(dir_bad_images, f"image_light_guiding_bad_pixels_{i+1}.fits")

        # Save the raw image in "images_generated" directory
        fits.writeto(raw_output_filename, raw_image, overwrite=True, header=fits.Header([
            (Telescope.keyword_image_type, Telescope.keyword_light_images),
            (Telescope.keyword_observation_date, FITSImage(fm.all_images[i]).date.strftime('%Y-%m-%dT%H:%M:%S.%f'))
        ]))

    for i in range(len(fm.all_darks)):
    
        raw_image = FITSImage(fm.all_darks[i]).data  # 1024x1024 image filled with ones

        if i%interval == 0 and i != 0:
            # Set hot pixel values
            raw_image[telegraphic_indices] = telegraphic_pixel_values
            # Set dead pixel values
            raw_image[telegraphic_indices] = telegraphic_pixel_values

        raw_output_filename = os.path.join(dir_bad_images, f"image_dark_guiding_bad_pixels_{i+1}.fits")

        # Save the raw image in "images_generated" directory
        fits.writeto(raw_output_filename, raw_image, overwrite=True, header=fits.Header([
            (Telescope.keyword_image_type, Telescope.keyword_dark_images),
            (Telescope.keyword_observation_date, FITSImage(fm.all_darks[i]).date.strftime('%Y-%m-%dT%H:%M:%S.%f'))
        ]))









