import cv2
import numpy as np
from openvino.runtime import Core


class EmotionRecognizer:
    '''
    TODO: add DocString
    '''

    def __init__(self, device: str = "CPU", model_xml: str = "model/FP32/emotions-recognition-retail-0003.xml",
                 weights_bin: str = "model/FP32/emotions-recognition-retail-0003.bin", verbose: bool = False):
        self.verbose = verbose

        # Initialize the Inference Engine and loadin the Model and Weights
        ie = Core()
        self.model = ie.read_model(model=model_xml,
                                   weights=weights_bin)
        self.model = ie.compile_model(model=self.model, device_name=device)

        # Getting the input layer information
        self.input_layer = next(iter(self.model.inputs))

        # Inference Mode
        self.model = self.model.create_infer_request()

    def predict(self, imgfile: str) -> int:
        input_shape = self.input_layer.shape
        img = self.preprocess(imgfile, input_shape)
        output = self.model.infer({self.input_layer.any_name: img})
        if self.verbose:
            print(output)
        return np.argmax(self.model.get_output_tensor().data)

    @staticmethod
    def preprocess(imgfile: str, input_shape: any):
        image = cv2.imread(imgfile)
        _, C, H, W = input_shape
        image = cv2.resize(image, (W, H))
        image = np.expand_dims(image.transpose(2, 0, 1), 0)
        return image


def main():
    # Example Code
    sample_img = "data/angry0.jpg"
    emotion_recognizer = EmotionRecognizer()
    output = emotion_recognizer.predict(sample_img)
    labels = ["neutral", "happy", "sad", "surprise", "anger"]
    print("Emotion:", labels[output])


if __name__ == "__main__":
    main()
