import io
from PIL import Image

format = 'png'

def pil2byte(img_pil):
    buffer = io.BytesIO()
    img_pil.save(buffer, format=format)
    img_byte_arr:bytes = buffer.getvalue()

    return img_byte_arr
 