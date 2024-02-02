from smart_crop import crop_image
import shutil
import time
from PIL import Image
from tqdm import tqdm
import ipywidgets as widgets
from io import BytesIO
import wget
import os
import subprocess
from pathlib import Path

# Set your directories here
INSTANCE_DIR = "/path/to/instance/dir"
CAPTIONS_DIR = "/path/to/captions/dir"
SESSION_DIR = "/path/to/session/dir"

# Download smart_crop.py if not present
os.chdir('/content')
if not os.path.exists("/content/smart_crop.py"):
    wget.download(
        'https://raw.githubusercontent.com/TheLastBen/fast-stable-diffusion/main/Dreambooth/smart_crop.py')

# Remove existing instance images and captions if set
# This needs to be set or passed as an argument
Remove_existing_instance_images = True
if Remove_existing_instance_images:
    if os.path.exists(INSTANCE_DIR):
        shutil.rmtree(INSTANCE_DIR)
    if os.path.exists(CAPTIONS_DIR):
        shutil.rmtree(CAPTIONS_DIR)

# Create instance and captions directories if they don't exist
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR, exist_ok=True)
if not os.path.exists(CAPTIONS_DIR):
    os.makedirs(CAPTIONS_DIR, exist_ok=True)

# Remove .ipynb_checkpoints directory if it exists
ipynb_checkpoints_path = os.path.join(INSTANCE_DIR, ".ipynb_checkpoints")
if os.path.exists(ipynb_checkpoints_path):
    shutil.rmtree(ipynb_checkpoints_path)

IMAGES_FOLDER_OPTIONAL = ""  # This should be set or passed as an argument

# Smart crop parameters
Smart_Crop_images = True
Crop_size = 512

# Code for handling IMAGES_FOLDER_OPTIONAL
if IMAGES_FOLDER_OPTIONAL != "":
    # Remove .ipynb_checkpoints directory if it exists
    ipynb_checkpoints_path = os.path.join(
        IMAGES_FOLDER_OPTIONAL, ".ipynb_checkpoints")
    if os.path.exists(ipynb_checkpoints_path):
        shutil.rmtree(ipynb_checkpoints_path)

    # Move .txt files from IMAGES_FOLDER_OPTIONAL to CAPTIONS_DIR
    for txt_file in glob.glob(os.path.join(IMAGES_FOLDER_OPTIONAL, "*.txt")):
        destination_path = os.path.join(
            CAPTIONS_DIR, os.path.basename(txt_file))
        shutil.move(txt_file, destination_path)

    if Smart_Crop_images:
        for filename in tqdm(os.listdir(IMAGES_FOLDER_OPTIONAL), bar_format='  |{bar:15}| {n_fmt}/{total_fmt} Uploaded'):
            extension = filename.split(".")[-1]
            new_path_with_file = os.path.join(INSTANCE_DIR, filename)
            file = Image.open(os.path.join(IMAGES_FOLDER_OPTIONAL, filename))
            if file.size != (Crop_size, Crop_size):
                image = crop_image(file, target_size=Crop_size)
                if extension.lower() == "jpg":
                    image = image.convert("RGB")
                    image.save(new_path_with_file, format="JPEG", quality=100)
                else:
                    image.save(new_path_with_file, format=extension.upper())
            else:
                shutil.copy(os.path.join(IMAGES_FOLDER_OPTIONAL,
                            filename), new_path_with_file)
    else:
        for filename in tqdm(os.listdir(IMAGES_FOLDER_OPTIONAL), bar_format='  |{bar:15}| {n_fmt}/{total_fmt} Uploaded'):
            source_path = os.path.join(IMAGES_FOLDER_OPTIONAL, filename)
            destination_path = os.path.join(INSTANCE_DIR, filename)
            shutil.copy(source_path, destination_path)

    print('\n\033[1;32mDone, proceed to the next cell')

# Functions for renaming files and zipping directories


def rename_files(directory):
    for path in Path(directory).rglob('* *'):
        if path.is_file():
            new_name = str(path).replace(' ', '-')
            os.rename(path, new_name)


def zip_directory(directory_name, zip_name):
    subprocess.run(['zip', '-r', zip_name, directory_name], check=True)


# Rename files and zip directories
rename_files(INSTANCE_DIR)
rename_files(CAPTIONS_DIR)
os.chdir(SESSION_DIR)
if os.path.exists("instance_images.zip"):
    os.remove("instance_images.zip")
if os.path.exists("captions.zip"):
    os.remove("captions.zip")
zip_directory("instance_images", "instance_images.zip")
zip_directory("captions", "captions.zip")
os.chdir('/content')
