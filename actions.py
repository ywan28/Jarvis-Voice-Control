from speech_utils import speak
import webbrowser
import subprocess
import os
from image_summarizer import jarvis_image_summarizer
import memory
from functools import wraps
import state
import pyautogui
from external_apis import get_weather as ext_get_weather, get_news as ext_get_news
from datetime import datetime
from stock_report import *

def store_interaction_decorator(func):
    @wraps(func)
    def wrapper(param, raw_command=None):
        if raw_command:
            memory.store_interaction(raw_command, param)
        return func(param)
    return wrapper

@store_interaction_decorator
def execute_search(param):
    speak(f"Searching for {param}")
    webbrowser.open(f"https://www.google.com/search?q={param}")

@store_interaction_decorator
def execute_open_url(param):
    speak(f"Opening {param}")
    webbrowser.open(param)

@store_interaction_decorator
def execute_open_app(param):
    app_name = param
    speak(f"Opening {app_name}")
    subprocess.run(["open", "-a", app_name])


@store_interaction_decorator
def execute_answer(param):
    speak(param)

@store_interaction_decorator
def execute_exit(_):
    speak("Exiting Jarvis.")
    exit()

@store_interaction_decorator
def execute_start_timer(param):
    speak(f"Starting timer for {param}")
    url = f"https://www.google.com/search?q=set+timer+for+{param.replace(' ', '+')}"
    webbrowser.open(url)

@store_interaction_decorator
def execute_volume_up(param):
    speak("Increasing volume.")
    os.system(f"osascript -e 'set volume output volume ((output volume of (get volume settings)) + {param}) --100%'")

@store_interaction_decorator
def execute_volume_down(param):
    speak("Decreasing volume.")
    os.system(f"osascript -e 'set volume output volume ((output volume of (get volume settings)) - {param}) --100%'")

@store_interaction_decorator
def execute_define(param):
    speak(param)

@store_interaction_decorator
def execute_sleep_jarvis(param):
    state.jarvis_awake = False
    speak("Going to sleep. Say 'Jarvis' to wake me up.")

def execute_summarize_screenshot(param, raw_command=None):
    extracted_text, summary = jarvis_image_summarizer()
    if extracted_text and summary:
        memory.store_interaction(extracted_text, summary)
    else:
        memory.store_interaction("No text extracted from image", "No explanation available")

@store_interaction_decorator
def execute_type(param):
    speak(f"Typing: {param}")
    pyautogui.typewrite(param, interval=0.05)

@store_interaction_decorator
def execute_click(param):
    speak("Clicking mouse.")
    pyautogui.click()

@store_interaction_decorator
def execute_move_mouse(param):
    try:
        x_str, y_str = param.split(',')
        x, y = int(x_str.strip()), int(y_str.strip())
        speak(f"Moving mouse to ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.3)
    except Exception as e:
        speak(f"Invalid coordinates provided for mouse movement: {param}")

@store_interaction_decorator
def execute_get_weather(param):
    return ext_get_weather(param)

@store_interaction_decorator
def execute_get_news(param):
    return ext_get_news(param)

@store_interaction_decorator
def tell_time(mode="time"):
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")           # e.g., 02:45 PM
    date_str = now.strftime("%B %d, %Y")          # e.g., July 29, 2025
    day_str = now.strftime("%A")                  # e.g., Tuesday

    if mode == "day":
        response = f"Today is {day_str}, {date_str}."
    elif mode == "time":
        response = f"The time is {time_str}."
    else:
        response = f"Today is {day_str}, {date_str}. The time is {time_str}."
    speak(response)


def get_stock_info(param=None, raw_command=None):
    if param is None:
        param = ["BTC-USD", "update from yesterday"]
    stock = param[0]
    command = param[1]
    data = get_stock_data(stock)
    report = generate_stock_report(data,command)
    speak(report)

ACTION_FUNCTIONS = {
    "search": execute_search,
    "open_url": execute_open_url,
    "open_app": execute_open_app,
    "answer": execute_answer,
    "exit": execute_exit,
    "start_timer": execute_start_timer,
    "volume_up": execute_volume_up,
    "volume_down": execute_volume_down,
    "define": execute_define,
    "sleep_jarvis": execute_sleep_jarvis,
    "summarize_screenshot": execute_summarize_screenshot,
    "type": execute_type,
    "click": execute_click,
    "move_mouse": execute_move_mouse,
    "get_weather": execute_get_weather,
    "get_news": execute_get_news,
    "get_time": tell_time,
    "stock_report": get_stock_info
}