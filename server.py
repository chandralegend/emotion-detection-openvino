import os
import time
import yaml
import dotenv
import argparse
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage
from utils import decodebase64, load_model

app = Flask(__name__)
api = Api(app, version='1.0-alpha', title='Emotion Recognizer API',
          description="Recognize Emotion of a given image.", default="Endpoints", default_label='Emotion Recognizer')
namespace = api.namespace('emotion', description='Emotion Recognizer')

upload_parser = reqparse.RequestParser()
upload_parser.add_argument('imgfile', type=FileStorage,
                           location='files', required=True)

secrets = dotenv.dotenv_values('.env')
is_production = secrets["SERVER_ENV"] == "PRODUCTION"
print("Running on Production: {}".format(is_production))

'''
Gunicorn doesnt run on __main__, so we need to initialize the inference here
'''
if is_production:
    with open('default.config.yaml', 'r') as stream:
        config = yaml.safe_load(stream)
    labels = config['labels']
    os.makedirs('temp', exist_ok=True)

    emotion_recognizer = load_model(
        namespace.logger, config['model_xml'], config['weights_bin'])


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
            os.remove(img_path)
        except Exception as e:
            namespace.logger.error(e)
            return jsonify({"error": str(e)}, 400)
        return jsonify({"emotion": labels[output]})


if (__name__ == "__main__") & (not is_production):
    '''Following Lines run only in development'''
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-p', '--port', default=5000,
                           type=int, help='port to listen on')
    argparser.add_argument(
        '--config', default="default.config.yaml", type=str, help='path to config file')
    argparser.add_argument('-d', '--debug', default=True,
                           action='store_true', help='enable debug mode')
    args = argparser.parse_args()

    with open(args.config, 'r') as stream:
        config = yaml.safe_load(stream)
    labels = config['labels']  # Label mappings
    os.makedirs('temp', exist_ok=True)

    emotion_recognizer = load_model(
        namespace.logger, config['model_xml'], config['weights_bin'])

    app.run(port=args.port, debug=args.debug)
