from PIL import Image
import io
import base64
import sys
import os

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

def load_model(logger, model_xml, weights_bin):
    '''Load the model'''
    try:
        from emotion_recognizer.model import EmotionRecognizer
        # check if the xml and bin files are present
        if not(os.path.isfile(model_xml) and os.path.isfile(weights_bin)):
            raise FileNotFoundError
        emotion_recognizer = EmotionRecognizer(
            model_xml=model_xml, weights_bin=weights_bin)
        logger.info("Emotion Recognizer loaded Successfully")
        return emotion_recognizer
    except ImportError:
        logger.critical("Emotion Recognizer not found.")
        sys.exit(1)
    except Exception as e:
        logger.critical(
            "Error loading Emotion Recognizer: {}".format(e))
        sys.exit(1)

