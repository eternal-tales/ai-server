import numpy as np
import cv2
import uuid

img_path = 'resources/assets/images/pets/'
img_format = ".png"

server_image_width = 1920
server_line_gap = 20

def read_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    return img


def transform_stretch(image_number, x_position, client_image_width, client_line_gap, resize=None):
    x_pos = int(x_position * ( (server_image_width - server_line_gap) / (client_image_width - client_line_gap)))
    img = cv2.imread(img_path+image_number+img_format)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    size = img.shape[:2][::-1][1]
    img = cv2.resize(img[:,x_pos:x_pos+server_line_gap],[server_image_width,server_image_width])
    if resize:
        img = cv2.resize(img,resize)
    return img

