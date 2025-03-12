import os
import re
import whisper
import torch
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Ensure PyTorch runs on CPU only
torch.set_default_device("cpu")

# Load Whisper model (small version for better performance)
model = whisper.load_model("small")

def mask_credit_card_numbers(text):
    """
    Redacts potential credit card numbers for PCI compliance.
    Replaces them with "***" while preserving the sentence structure.
    """
    # Credit card regex patterns (Visa, MasterCard, AMEX, Discover)
    credit_card_pattern = r'\b(?:\d[ -]*?){13,16}\b'

    # Replace detected card numbers with "***"
    masked_text = re.sub(credit_card_pattern, "***", text)

    return masked_text

@app.route('/', methods=['GET', 'POST'])
def index():
    transcription = None
    call_reason = None

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template("index.html", transcription="No file uploaded.")

        file = request.files['file']
        if file.filename == '':
            return render_template("index.html", transcription="No file selected.")

        file_path = os.path.join("temp_audio.wav")
        file.save(file_path)

        try:
            # Transcribe audio
            result = model.transcribe(file_path)
            transcription = result.get('text', '')

            # Mask credit card numbers
            transcription = mask_credit_card_numbers(transcription)

            # Identify reason for the call
            call_reason = determine_call_reason(transcription)

            # Clean up temporary file
            os.remove(file_path)

        except Exception as e:
            transcription = f"Error: {str(e)}"

    return render_template("index.html", transcription=transcription, call_reason=call_reason)


def determine_call_reason(transcription):
    """
    Basic function to determine the reason for the call based on keywords.
    """
    keywords = {
        "billing": ["bill", "payment", "charged", "invoice"],
        "technical support": ["not working", "error", "crash", "support"],
        "customer service": ["speak to a representative", "help", "question", "customer support"],
    }

    for category, words in keywords.items():
        if any(word in transcription.lower() for word in words):
            return f"The call is related to {category}."

    return "Unable to determine the call reason."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
