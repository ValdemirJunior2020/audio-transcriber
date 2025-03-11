import whisper
import re
import math

# Load Whisper model
model = whisper.load_model("small")

def mask_credit_cards(text):
    """Mask credit card numbers for PCI compliance."""
    return re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '**', text)

def highlight_text(text):
    """Highlight request IDs (6+ digit numbers) and emails in red & bold."""
    
    # Highlight request IDs (Assuming they are numeric and at least 6 digits long)
    text = re.sub(r'(\b\d{6,}\b)', r'<span style="color:red; font-weight:bold;">\1</span>', text)

    # Highlight emails (e.g., user@example.com)
    text = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,7})', 
                  r'<span style="color:red; font-weight:bold;">\1</span>', text, flags=re.IGNORECASE)

    return text

def extract_call_reason(text):
    """Extracts the reason for the call using keyword-based analysis."""
    keywords = [
        "voucher", "reservation", "refund", "cancellation", "billing issue",
        "account problem", "technical support", "payment issue", "credit card",
        "claim", "warranty", "complaint", "booking"
    ]
    
    reason_sentences = []
    
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    for sentence in sentences:
        for keyword in keywords:
            if keyword in sentence.lower():
                reason_sentences.append(sentence.strip())
                break  # Avoid duplicates

    if reason_sentences:
        return f'<span style="color:blue; font-weight:bold;">{" ".join(reason_sentences)}</span>'

    return "No clear reason detected."

def split_by_time(transcription, duration):
    """Splits transcription into timestamped chunks."""
    words = transcription.split()
    words_per_minute = max(1, len(words) // math.ceil(duration / 60))  # Ensure words per segment
    time_chunks = [words[i:i + words_per_minute] for i in range(0, len(words), words_per_minute)]

    formatted_chunks = []
    for i, chunk in enumerate(time_chunks):
        timestamp = f"{int((i * 60) / 60):02}:{int((i * 60) % 60):02}"  # Convert to hh:mm:ss format
        formatted_chunks.append(f'<b style="color:purple;">[{timestamp}]</b> ' + " ".join(chunk))

    return "<br>".join(formatted_chunks)

def transcribe_audio(file_path):
    """Transcribes audio, processes text, and extracts additional details."""
    result = model.transcribe(file_path)
    text = result["text"]
    duration = result["segments"][-1]["end"]  # Get audio duration from Whisper

    # Process text
    text = mask_credit_cards(text)
    text = highlight_text(text)
    
    # Extract details
    call_reason = extract_call_reason(text)
    formatted_text = split_by_time(text, duration)

    return formatted_text, call_reason
