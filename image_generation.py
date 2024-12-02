import cabaret
import numpy as np
import os
import random
from astropy.io import fits
from prose import Telescope
from datetime import datetime, timedelta
import shutil

def generate_light_images(ra, dec, exposure_time, base_date, num_pixels_shift, num_light_images, seeing_data, camera, telescope, dir_base_images_light = 'images_generated_light_guiding'):
    """
    Generate an image of the sky at a given RA and Dec.

    Parameters
    ----------
    ra : float
        Right Ascension of the object in degrees.
    dec : float
        Declination of the object in degrees.
    exposure_time : float
        Exposure time of the image in seconds.
    base_date : datetime of the first observation.
        Date and time of the observation.
    num_pixels_shift : int
        Number of pixels to include in the image.
    """

    camera.plate_scale = (np.arctan((camera.pitch * 1e-6) / (telescope.focal_length)) * (180 / np.pi) * 3600)  # "/pixel

    degree_per_pixel = camera.plate_scale/3600

    ra_min, ra_max   = ra  - num_pixels_shift*degree_per_pixel, ra  + num_pixels_shift*degree_per_pixel
    dec_min, dec_max = dec - num_pixels_shift*degree_per_pixel, dec + num_pixels_shift*degree_per_pixel

    # Generate random RA and Dec values
    random_ras = [random.uniform(ra_min, ra_max) for _ in range(num_light_images)]
    random_decs = [random.uniform(dec_min, dec_max) for _ in range(num_light_images)]

    # Directory to save light images
    os.makedirs(dir_base_images_light, exist_ok=True) # Create directory if it doesn't exist

    # Generate light images
    for i in range(num_light_images):
        curr_date = base_date + timedelta(seconds=i*exposure_time) #interval between each image = exposure time
        site = cabaret.Site(seeing=seeing_data[i])

        light = cabaret.generate_image(random_ras[i], random_decs[i], exposure_time, dateobs=curr_date, camera=camera, site=site)
        raw_output_filename = os.path.join(dir_base_images_light, f"raw_image_light_{i+1}.fits")

        # Save the raw image in "images_generated" directory
        fits.writeto(raw_output_filename, light, overwrite=True, header=fits.Header([
            (Telescope.keyword_image_type, Telescope.keyword_light_images),
            (Telescope.keyword_observation_date, curr_date.strftime('%Y-%m-%dT%H:%M:%S.%f'))
        ]))

def generate_dark_images(ra, dec, exposure_time, base_date, num_dark_images, num_light_images, seeing_data, camera, dir_base_images_dark = 'images_generated_dark_guiding'):
    """
    Generate an image of the sky at a given RA and Dec.

    Parameters
    ----------
    ra : float
        Right Ascension of the object in degrees.
    dec : float
        Declination of the object in degrees.
    exposure_time : float
        Exposure time of the image in seconds.
    base_date : datetime of the first observation.
        Date and time of the observation.
    num_pixels_shift : int
        Number of pixels to include in the image.
    """

    # Directory to save dark images
    os.makedirs(dir_base_images_dark, exist_ok=True) # Create directory if it doesn't exist
    base_date = base_date + timedelta(seconds=num_light_images*exposure_time) # Start generating dark images after light images
    
    # Generate dark images
    for i in range(num_dark_images):
        curr_date = base_date + timedelta(seconds=i*exposure_time) #interval between each image = exposure time
        site = cabaret.Site(seeing=seeing_data[i+num_light_images])
        
        dark = cabaret.generate_image(ra, dec, exposure_time, dateobs=curr_date, light=0, camera=camera, site=site)
        raw_output_filename = os.path.join(dir_base_images_dark, f"raw_image_dark_{i+1}.fits")

        # Save the raw image in "images_generated" directory
        fits.writeto(raw_output_filename, dark, overwrite=True, header=fits.Header([
            (Telescope.keyword_image_type, Telescope.keyword_dark_images),
            (Telescope.keyword_observation_date, curr_date.strftime('%Y-%m-%dT%H:%M:%S.%f'))
        ]))


def combine_folders(dir_base_images_light, dir_base_images_dark, dir_base_images_all = 'images_all_guiding_pixels'):

    # Directory to save all images
    os.makedirs(dir_base_images_all, exist_ok=True)  # Create directory if it doesn't exist

    # Copy contents of 'images_generated_dark' and 'images_generated_light' into 'images_generated_all'

    for filename in os.listdir(dir_base_images_light):
        shutil.copy(os.path.join(dir_base_images_light, filename), dir_base_images_all)
        
    for filename in os.listdir(dir_base_images_dark):
        shutil.copy(os.path.join(dir_base_images_dark, filename), dir_base_images_all)


def delete_files_in_folder(folder_path):
    """
    Deletes all files in the specified folder.

    Parameters:
    folder_path (str): The path to the folder where files need to be deleted.
    """
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Iterate over all the files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                # Check if it is a file and delete it
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        print(f'The folder {folder_path} does not exist.')