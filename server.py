import os
import sys
import time
import yaml
import dotenv
import argparse
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from utils import decodebase64

app = Flask(__name__)
api = Api(app, version='1.0-alpha', title='Emotion Recognizer API',
          description="Recognize Emotion of a given image.", default="Endpoints", default_label='Emotion Recognizer')
namespace = api.namespace('emotion', description='Emotion Recognizer')

upload_parser = reqparse.RequestParser()
upload_parser.add_argument('imgfile', type=FileStorage,
                           location='files', required=True)

secrets = dotenv.dotenv_values('.env')
is_production = secrets["SERVER_ENV"] == "PRODUCTION"
print("Production:", is_production)


@api.route('/emotion/base64', methods=["POST"], endpoint="base64")
@api.doc(responses={
    200: 'Successful Emotion Detection',
    400: 'Bad request',
    500: 'Internal server error.'},
    description="Detect Emotion of an Image in Base64 format")
class EmotionDetectionBase64(Resource):
    base64_request = api.model("Base64 Emotion Detection Endpoint", {
        "img": fields.String(required=True, description="Base64 encoded image")
    })

    @api.expect(base64_request)
    def post(self):
        image = request.json["img"]
        try:
            # decoding the base64 image and saving
            image = decodebase64(image)
            img_path = "temp/temp_{}.png".format(time.time())
            image.save(img_path)
            # predicting the emotion
            output = emotion_recognizer.predict(img_path)
            os.remove(img_path)
        except Exception as e:
            namespace.logger.error(e)
            return jsonify({"error": str(e)}, 400)
        return jsonify({"emotion": labels[output]})


@api.route('/emotion', methods=["POST"])
@api.doc(responses={
    200: 'Successful Emotion Detection',
    400: 'Bad request',
    500: 'Internal server error.'},
    description="Detect Emotion of an Uploaded Image")
class EmotionDetection(Resource):

    @api.expect(upload_parser)
    def post(self):
        uploads = upload_parser.parse_args()
        img_path = "temp/temp_{}.png".format(time.time())
        try:
            uploads["imgfile"].save(img_path)
            output = emotion_recognizer.predict(img_path)
            # os.remove(img_path)
        except Exception as e:
            namespace.logger.error(e)
            return jsonify({"error": str(e)}, 400)
        return jsonify({"emotion": labels[output]})


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-p', '--port', default=5000,
                           type=int, help='port to listen on')
    argparser.add_argument(
        '--config', default="default.config.yaml", type=str, help='path to config file')
    argparser.add_argument('-d', '--debug', default=False,
                           action='store_true', help='enable debug mode')
    args = argparser.parse_args()

    with open('default.config.yaml', 'r') as stream:
        config = yaml.safe_load(stream)

    # Label mappings
    labels = config['labels']

    os.makedirs('temp', exist_ok=True)

    try:
        from emotion_recognizer.model import EmotionRecognizer
        # check if the xml and bin files are present
        if not(os.path.isfile(config['model_xml']) and os.path.isfile(config['weights_bin'])):
            raise FileNotFoundError
        emotion_recognizer = EmotionRecognizer(
            model_xml=config['model_xml'], weights_bin=config['weights_bin'])
        namespace.logger.info("Emotion Recognizer loaded Successfully")
    except ImportError:
        namespace.logger.critical("Emotion Recognizer not found.")
        sys.exit(1)
    except Exception as e:
        namespace.logger.critical(
            "Error loading Emotion Recognizer: {}".format(e))
        sys.exit(1)

    if is_production:
        app.run(host='0.0.0.0', port=args.port, debug=args.debug)
    else:
        app.run(port=args.port, debug=True)
