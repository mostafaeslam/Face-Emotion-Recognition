import os
import numpy as np
import cv2
from keras.models import model_from_json
from flask import Flask, request, render_template, redirect, url_for, jsonify
from keras.mixed_precision import set_global_policy

# Initialize Flask app 
app = Flask(__name__)

# Define paths to files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
MODEL_JSON_PATH = os.path.join(MODEL_DIR, 'model.json')
MODEL_H5_PATH = os.path.join(MODEL_DIR, 'model.h5')
CASCADE_PATH = os.path.join(MODEL_DIR, 'haarcascade_frontalface_default.xml')
STATIC_DIR = os.path.join(BASE_DIR, 'app', 'static')
first_time = True

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
    
    global first_time
    if first_time:
        first_time = False
        return render_template('index.html', emotion="Upload an image")


    if request.method == 'POST':
        # Save uploaded image
        file = request.files['image']
        if file:
            file_path = os.path.join(STATIC_DIR, 'output.jpg')
            file.save(file_path)

            # Process the uploaded image
            emo = process_image(file_path)
            if emo:
                return render_template("index.html", emotion=emo) 
            else:
                return  render_template("index.html", emotion="Error processing image") 

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
        
        face = faces[0]
        (x, y, w, h) = face

        # Predict emotion for each detected face
        face = gray[y:y + h, x:x + w]
        face = cv2.resize(face, (48, 48))
        face = face.reshape(1, 48, 48, 1) / 255.0

        # Predict emotion using the model
        prediction = model.predict(face)
        emotion = np.argmax(prediction)
        emotion_detection = ('Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral') # list of emotions

        # Return the detected emotion
        return emotion_detection[emotion]

    except Exception as e:
        print(f"Error processing image: {e}") 
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    