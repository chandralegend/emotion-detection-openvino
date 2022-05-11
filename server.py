import os
import sys
import time
import io
import logging
import base64
from tkinter import Image
import dotenv
import argparse
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields

secrets = dotenv.dotenv_values('.env')
logger = logging.getLogger(__name__)

app = Flask(__name__)

app_swagger = Api(app, version='1.0-alpha', title='Emotion Recognizer API')
namespace = app_swagger.namespace('', description='promiseQ AI')

is_prod = secrets["SERVER_ENV"] == "PRODUCTION"


@namespace.route('/emotion/base64', methods=["POST"])
class EmotionDetectionBase64(Resource):
    base64_request = app_swagger.model("Base64 Emotion Detection Endpoint", {
        "img": fields.String(required=True, description="Base64 encoded image")
    })

    @app_swagger.expect(base64_request)
    def post(self):
        image = request.json["img"]
        try:
            # decoding the base64 image and saving
            image = base64.b64decode(image)
            image = Image.open(io.BytesIO(image)).convert('RGBA')
            image = self.pure_pil_alpha_to_color_v2(image)
            '''using current time to makesure that model wont be
            using a previous saved image'''
            img_path = "temp_{}.png".format(time.time())
            image.save(img_path)
            # predicting the emotion
            output = emotion_recognizer.predict(img_path)
            os.remove(img_path)
        except Exception as e:
            logger.error(e)
            if not is_prod:
                return jsonify({"error": str(e)})
        return jsonify({"emotion": labels[output]})

    @staticmethod
    def pure_pil_alpha_to_color_v2(image, color=(255, 255, 255)):
        image.load()
        background = Image.new('RGB', image.size, color)
        background.paste(image, mask=image.split()[3])
        return background


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-p', '--port', default=5000,
                           type=int, help='port to listen on')
    argparser.add_argument(
        '--xml', default="emotion_recognizer/model/FP32/emotions-recognition-retail-0003.xml", type=str, help='path to model xml')
    argparser.add_argument(
        '--bin', default="emotion_recognizer/model/FP32/emotions-recognition-retail-0003.bin", type=str, help='path to model bin')
    argparser.add_argument('-d', '--debug', default=False,
                           action='store_true', help='enable debug mode')
    args = argparser.parse_args()

    labels = ["Neutral", "Happy", "Sad", "Surprise", "Anger"]
    os.makedirs('/temp', exist_ok=True)

    try:
        from emotion_recognizer.model import EmotionRecognizer
        # check if the xml and bin files are present
        if not(os.path.isfile(args.xml) and os.path.isfile(args.bin)):
            raise FileNotFoundError
        emotion_recognizer = EmotionRecognizer(
            model_xml=args.xml, model_bin=args.bin)
        logger.critical("Emotion Recognizer loaded Successfully")
    except ImportError:
        logger.critical("Emotion Recognizer not found.")
        sys.exit(1)
    except Exception as e:
        logger.critical("Error loading Emotion Recognizer: {}".format(e))
        sys.exit(1)

    if is_prod:
        app_swagger.init_app(app)
        app.run(host='0.0.0.0', port=args.port, debug=args.debug)
    else:
        app.run(host='localhost', port=args.port, debug=args.debug)
