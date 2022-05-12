from PIL import Image
import io
import base64

def pure_pil_alpha_to_color_v2(image, color=(255, 255, 255)):
    '''Convert PIL image to RGBA'''
    image.load()
    background = Image.new('RGB', image.size, color)
    background.paste(image, mask=image.split()[3])
    return background

def decodebase64(image):
    '''Decode base64 image'''
    image = base64.b64decode(image)
    image = Image.open(io.BytesIO(image)).convert('RGBA')
    image = pure_pil_alpha_to_color_v2(image)
    return image
