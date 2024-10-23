import os
import numpy as np
import cv2
from tensorflow.keras.models import model_from_json
from flask import Flask, request, render_template, redirect, url_for, jsonify
from tensorflow.keras.mixed_precision import set_global_policy



# Initialize Flask app
app = Flask(__name__)

# Define paths to files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_JSON_PATH = os.path.join(BASE_DIR, 'model.json')
MODEL_H5_PATH = os.path.join(BASE_DIR, 'model.h5')
CASCADE_PATH = os.path.join(BASE_DIR, 'haarcascade_frontalface_default.xml')

# Load the model architecture and weights
set_global_policy('float32')
print("Loading model...")
with open(MODEL_JSON_PATH, 'r') as json_file:
    model = model_from_json(json_file.read())
    
model.load_weights(MODEL_H5_PATH)
print("Model loaded successfully.")

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

# Route for homepage with image upload
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Save uploaded image
        file = request.files['image']
        if file:
            file_path = os.path.join('static', 'output.jpg')
            file.save(file_path)

            # Process the uploaded image
            emo = process_image(file_path)
            if emo:
                return render_template("index.html", mass=emo) 
            else:
                return  render_template("index.html", mass="Error processing image") 

    return render_template('index.html')

# Helper function to process the image and predict emotion
def process_image(image_path):
    try:
        # Load image and convert to grayscale
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces using Haar cascade
        
        
        label = None
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) !=1:
            return label
        app.logger.info(f"Detected {len(faces)} faces in image")
        
        face = faces[0]
        (x, y, w, h) = face


        # Predict emotion for each detected face
        face = gray[y:y + h, x:x + w]
        face = cv2.resize(face, (48, 48))
        face = face.reshape(1, 48, 48, 1) / 255.0

        # Predict emotion using the model
        prediction = model.predict(face)
        emotion = np.argmax(prediction)
        emotion_detection = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral') # list of emotions

        # Annotate image with predicted emotion
        label = f'Emotion: {emotion_detection[emotion]}'

        # Save the processed image
        app.logger.info(f"Emotion detected: {label}")
        return label

    except Exception as e:
        print(f"Error processing image: {e}")
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    