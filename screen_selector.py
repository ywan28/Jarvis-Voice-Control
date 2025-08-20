import subprocess
import time
from openai import OpenAI
from PIL import Image
import pytesseract
import pyttsx3

client = OpenAI(api_key="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")

# ---------- Speak ----------
def speak(text, voice_index=14, rate=180):
    print(f"[Jarvis] {text}")
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if 0 <= voice_index < len(voices):
        engine.setProperty('voice', voices[voice_index].id)
    engine.setProperty('rate', rate)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

# ---------- Screenshot Capture ----------
def capture_window_native(filename="screenshot.png"):
    subprocess.run(["screencapture", "-i", filename])
    print(f"[System] Screenshot saved to {filename}")
    return filename

# ---------- OCR Extraction ----------
def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    print("[OCR Extracted Text]")
    print(text)
    return text.strip()

# ---------- GPT Summarizer ----------
def summarize_text_with_gpt(text):
    prompt = f"Please explain the following text simply and clearly. Try to keep the summary under 50 words:\n\n{text}\n\nExplanation:"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Jarvis, a concise AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = response.choices[0].message.content.strip()
        print(f"[Jarvis Summary] {summary}")
        return summary
    except Exception as e:
        print(f"[GPT Error] {e}")
        return "Sorry, I couldn't process the explanation."

# ---------- Main Flow ----------
def jarvis_image_summarizer():
    speak("Ready to capture the image you want me to explain.")
    screenshot_path = capture_window_native()
    time.sleep(1)
    extracted_text = extract_text_from_image(screenshot_path)
    if extracted_text:
        speak("Analyzing the captured text.")
        summary = summarize_text_with_gpt(extracted_text)
        speak(summary)
    else:
        speak("I couldn't find any text to analyze in the captured image.")

if __name__ == "__main__":
    jarvis_image_summarizer()
