import json
import os

CONFIG_FILE = "config.json"

# Load config from file or use defaults
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "wake_word": "jarvis",
        "wake_timeout": 10,
        "voice": 14,
        "tts_speed": 180,
        "default_location": "",
        "default_stocks": [],
        "default_news_topics": [],
        "openai_api_key": "",
        "openweather_api_key": ""
    }

# Save updated config
def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
