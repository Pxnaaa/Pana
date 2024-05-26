from flask import Flask, render_template, request, flash, redirect, session, url_for
import os
from werkzeug.utils import secure_filename
import sys
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from keras.utils import custom_object_scope
import keras
from tensorflow.keras.models import load_model
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
app = Flask(__name__)
app.secret_key = "kkkkk"

# Ensure the upload directory exists
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def process_image(filename):
    # Dummy image processing function for illustration
    return f"Processed {filename}"

@app.route("/")
def index():
    print("YES", file=sys.stderr)
    print("---------------", file=sys.stderr)
    return render_template("index.html")

@app.route("/greet", methods=["POST", "GET"])
def greet():
    flash("Hi " + str(request.form['name_input']) + ", great")
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect(request.url)

    file = request.files['file']
    print(file, file=sys.stderr)

    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['filepath'] = filename  # Store the file path in the session
        print(f"Saved filepath in session: {filepath}", file=sys.stderr)
        print("---------------", file=sys.stderr)
        return redirect(url_for('results'))  # Redirect to the results page

    return render_template("index.html", button_text='No upload')

@app.route("/results")
def results():
    filepath = session.get('filepath')  # Retrieve the file path from the session
    
    print(filepath, file=sys.stderr)

    rel_filepath = f".\\static\\uploads\\{filepath}"

    print(rel_filepath, file=sys.stderr)
    x = classify_upload(rel_filepath)
    print(x, file=sys.stderr)
    if filepath:
        # Perform any image processing or analysis here
        # based on the file path or the image data
        result = process_image(filepath)
        return render_template("results.html", result=result)
    else:
        return render_template("results.html")




def classify_upload(rel_filepath):
    def load_model(path):
        model = models.inception_v3(pretrained=True)
        num_classes = 23  # Replace with your actual number of classes
        num_ftrs = model.AuxLogits.fc.in_features
        model.AuxLogits.fc = nn.Linear(num_ftrs, num_classes)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, num_classes)
        model.load_state_dict(torch.load(path, map_location=device))
        model = model.to(device)
        model.eval()
        return model
    
    def process_image(image_path):
        image = Image.open(image_path).convert('RGB')
        transformations = transforms.Compose([
            transforms.Resize((299, 299)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        image_tensor = transformations(image).unsqueeze(0)  # Add batch dimension
        return image_tensor.to(device)


    def predict_image(model, image_tensor):
        with torch.no_grad():
            outputs = model(image_tensor)
            _, predicted = torch.max(outputs, 1)
            return predicted.item()  # Return the index of the predicted class
    image_path = rel_filepath

    model = load_model("Final_Model_FINAL.pth")
    image_tensor = process_image(image_path)
    class_index = predict_image(model, image_tensor)
    class_indices = {
        'Clams': 0, 'Corals': 1, 'Crabs': 2, 'Dolphin': 3, 'Eel': 4, 'Fish': 5, 'Jelly Fish': 6, 'Lobster': 7, 
        'Nudibranchs': 8, 'Octopus': 9, 'Otter': 10, 'Penguin': 11, 'Puffers': 12, 'Sea Rays': 13, 'Sea Urchins': 14, 
        'Seahorse': 15, 'Seal': 16, 'Sharks': 17, 'Shrimp': 18, 'Squid': 19, 'Starfish': 20, 'Turtle_Tortoise': 21, 
        'Whale': 22
    }
    predicted_class_label = list(class_indices.keys())[list(class_indices.values()).index(class_index)]

    print(predicted_class_label, file=sys.stderr)
    print("---------------", file=sys.stderr)
    
    return predicted_class_label

if __name__ == '__main__':
    app.run(debug=True)
