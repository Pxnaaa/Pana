from flask import Flask, render_template, request, flash, redirect, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "kkkkk"

@app.route("/hello")
def index():
    
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

    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join('static/uploads', filename))
        session['filename'] = filename  # Store the filename in the session
        return redirect('/results')  # Redirect to the results page

    return render_template("index.html", button_text='No upload')

@app.route("/results")
def results():
    
    filename = session.get('filename')  # Retrieve the filename from the session
    print(filename)
    if filename:
        # Perform any image processing or analysis here
        # based on the filename or the image data
        result = process_image(filename)
        return render_template("results.html", result=result)
    else:
        return render_template("results.html")