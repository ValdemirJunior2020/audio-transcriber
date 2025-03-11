import os
import webbrowser
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from transcribe import transcribe_audio  

app = Flask(__name__, template_folder="templates")

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]

        if file.filename == "":
            return "No selected file"

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Process the file with Whisper
            transcription, call_reason = transcribe_audio(filepath)

            return render_template("index.html", transcription=transcription, call_reason=call_reason)

    return render_template("index.html", transcription=None, call_reason=None)

if __name__ == "__main__":
    # Automatically open the web browser when the app starts
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)
