import whisper
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Reduce memory usage by switching to Whisper "small"
model = whisper.load_model("small")

# Ensure PyTorch runs on CPU only
torch.set_default_device("cpu")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    file_path = "temp_audio.wav"
    file.save(file_path)

    try:
        result = model.transcribe(file_path)
        return jsonify({"transcription": result['text']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
