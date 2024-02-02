# Install and import requirements

import torch
import diffusers
from PIL import Image

from torch import autocast
from diffusers import StableDiffusionPipeline

# ------------------------------------------------------


def image_grid(imgs, rows, cols):
    assert len(imgs) == rows*cols

    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols*w, rows*h))
    grid_w, grid_h = grid.size

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols*w, i//cols*h))
    return grid


# ------------------------------------------------------

# Load the model
def load_model(model_id):
    # model_id = "sd-dreambooth-library/cat-toy"  # @param {type:"string"}
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, torch_dtype=torch.float16).to("cpu")
    return pipe


# ------------------------------------------------------

# Run the Stable Diffusion pipeline on Colab
# Don't forget to use the `sks` token in your prompt

def generate(prompt):
    # prompt = "a photo of sks toy floating on a ramen bowl" #@param {type:"string"}

    pipe = load_model(model_id='dhdbsrlw/zero-wearing-pink-clothes')

    num_samples = 1  # @param {type:"number"}
    num_rows = 1  # @param {type:"number"}

    all_images = []
    for _ in range(num_rows):
        images = pipe(prompt, num_images_per_prompt=num_samples,
                      num_inference_steps=50, guidance_scale=7.5).images
        all_images.extend(images)

    grid = image_grid(all_images, num_samples, num_rows)
    return grid


image = generate('a photo of sks zero running the park')
print(image)
