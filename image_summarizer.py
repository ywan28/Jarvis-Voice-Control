import subprocess
import time
from openai import OpenAI
from PIL import Image
import pytesseract
from speech_utils import speak
from config_manager import load_config

config = load_config()
OPENAI_API_KEY = config.get("openai_api_key", "")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
def capture_window_native(filename="screenshot.png"):
    subprocess.run(["screencapture", "-i", filename])
    return filename

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text.strip()

def summarize_text_with_gpt(text):
    prompt = f"Explain this simply in under 50 words:\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are Jarvis, a concise explainer."}, {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def jarvis_image_summarizer():
    speak("Ready to capture the image you want explained.")
    screenshot_path = capture_window_native()
    time.sleep(1)
    extracted_text = extract_text_from_image(screenshot_path)
    if extracted_text:
        speak("Analyzing captured text.")
        summary = summarize_text_with_gpt(extracted_text)
        speak(summary)
        return extracted_text, summary  # return both pieces
    else:
        speak("No readable text found in the captured image.")
        return None, None
