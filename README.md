Flask OpenVINO - Emotion Detection API
==============================

This project provides a rest api, where you can send image as multipart data/ in base64 string format to 2 seperate endpoints and endpoint will provide the emotion as of the person in the image.

Getting Started
------------
1. Clone the Repository
2. Install the Dependancies using `pip install -r requirements.txt` 
3. Run the server in development environment using `python3 server.py`

You can change the served port by using the  `--port 3000` argument after *server.py*. `--debug ` to enable debugging and if you have a different configuration file, you can use `--config <path/to/config.yaml>`.

4. To test the API you can use the integrated Swagger UI by going to the link shown in the terminal. Probably will be `http://127.0.0.1:5000` or using Curl.

Endpoints
------------
* `/emotion`
  * use multipart form in postman or any other api client and add a parameter called 'imgfile' and upload your image file
* `/emotion/base64`
  * Convert the image using a base64 converter https://codebeautify.org/image-to-base64-converter
  * and create json body with 'img' and paste the base64 string of the image you selected.
  
  and execute the request. if the request was successful, you will receive a json response in the format of `{"emotion": "surprise"}`

Todos
------------
- [ ] Docker Integration
- [ ] Elastic APM to Track the Performance
- [ ] Better Emotion Detection Model (This model is shit.)