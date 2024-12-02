import prose
import cabaret
import numpy as np
import matplotlib.pyplot as plt
import os

from matplotlib.animation import FuncAnimation
from astropy.io import fits
from prose import Telescope, FITSImage, FitsManager, Sequence, blocks
from datetime import datetime, timedelta



fm = FitsManager("./images_generated_light_guiding", depth=1)
ref =FITSImage(fm.all_images[0]) 


# Assume you have a list of 100 NumPy arrays (1024x1024)
# Replace this with your actual data
num_frames = len(fm.all_images)

images = []
for i in range(len(fm.all_images)):
    images.append(FITSImage(fm.all_images[i]).data)
    
import numpy as np
import cv2
from PIL import Image

# Example list of 100 NumPy arrays (replace this with your actual data)
frames = images

# Normalize frames to 8-bit range (0-255)
frames_normalized = [(frame - frame.min()) / (frame.max() - frame.min()) * 255 for frame in frames]
frames_normalized = [frame.astype(np.uint8) for frame in frames_normalized]

# Convert NumPy arrays to PIL Image objects
images = [Image.fromarray(frame) for frame in frames_normalized]

# Save as an animated GIF
output_file = "output.gif"
images[0].save(
    output_file,
    save_all=True,
    append_images=images[1:],  # Add the rest of the frames
    duration=100,  # Duration for each frame in milliseconds (adjust as needed)
    loop=0  # Infinite loop
)

print(f"GIF saved as {output_file}")
