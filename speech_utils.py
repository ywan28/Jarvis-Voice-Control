import json
import pyttsx3
import speech_recognition as sr
import threading

CONFIG_FILE = "config.json"

# Lock to prevent overlapping speech
_speak_lock = threading.Lock()

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def speak(text):
    """Speak text without overlapping previous speech."""
    with _speak_lock:  # ensures only one speak() runs at a time
        engine = pyttsx3.init()
        config = load_config()
        voice_index = config.get("voice", 14)
        rate = config.get("tts_speed", 200)

        print(f"[{config.get('wake_word', 'Jarvis').capitalize()}] {text}")
        voices = engine.getProperty('voices')
        if 0 <= voice_index < len(voices):
            engine.setProperty('voice', voices[voice_index].id)
        engine.setProperty('rate', rate)
        engine.setProperty('volume', 1.0)

        engine.say(text)
        engine.runAndWait()


def listen_for_command():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=0, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            return None
    try:
        command = recognizer.recognize_google(audio)
        print(f"[Voice] Heard: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("[Voice] Could not understand audio.")
    except sr.RequestError as e:
        print(f"[Voice] API error: {e}")
    return None

