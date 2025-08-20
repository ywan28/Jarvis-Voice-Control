# external_apis.py
import requests
import feedparser
import urllib.request
import ssl
import certifi
from openai import OpenAI

from speech_utils import speak
from config_manager import load_config

# Load keys from config
config = load_config()
OPENWEATHER_API_KEY = config.get("openweather_api_key", "")
OPENAI_API_KEY = config.get("openai_api_key", "")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# --- Weather ---
def get_weather(param):
    location = param or "Pennington,NJ,US"
    speak(f"Fetching weather for {location}...")
    if not OPENWEATHER_API_KEY:
        speak("Weather API key is missing. Please update settings.")
        return "Missing Weather API key."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=imperial"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("weather"):
            desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            msg = f"The weather in {location} is {desc} with a temperature of {temp}°F and humidity of {humidity}%."
            speak(msg)
            return msg
        else:
            speak("I couldn't get the weather for that location.")
            return "Weather fetch failed."
    except Exception as e:
        speak("Error fetching weather data.")
        print(f"[Weather Error] {e}")
        return "Error."


# --- News ---
def get_news(param=None):
    topic = param or "top news"
    topic_query = topic.strip().replace(" ", "+")
    rss_url = f"https://news.google.com/rss/search?q={topic_query}"

    speak(f"Fetching the latest {topic} news...")

    context = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(
        rss_url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )

    try:
        with urllib.request.urlopen(req, context=context) as response:
            data = response.read()

        feed = feedparser.parse(data)

        if not feed.entries:
            speak("I couldn't fetch any news at the moment.")
            return "News fetch failed."

        headlines = [entry.title for entry in feed.entries[:10]]
        joined_headlines = "\n".join(headlines)

        prompt = f"""
Explain the major ideas of these headlines." 
Also try to include any statistics.
Keep the response brief in one coherent paragraph under 50 words.
{joined_headlines}
        """

        if not OPENAI_API_KEY:
            speak("OpenAI API key is missing. Please update settings.")
            return "Missing OpenAI API key."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        summary = response.choices[0].message.content.strip()
        speak(summary)
        return summary

    except Exception as e:
        speak("Error fetching or summarizing news.")
        print(f"[News Error] {e}")
        return "Error fetching news."
