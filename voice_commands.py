# voice_commands.py
from speech_utils import speak, listen_for_command
from ai_parser import parse_command_with_ai
from actions import ACTION_FUNCTIONS
from config_manager import load_config
import time
import state

state.jarvis_awake = False
last_command_time = 0


def process_command(command: str):
    """Send a command string to the AI parser and execute resulting actions."""
    global last_command_time
    if not command.strip():
        return

    last_command_time = time.time()
    parsed = parse_command_with_ai(command)
    steps = parsed.get("steps", [])
    for step in steps:
        action = step.get("action")
        param = step.get("param", "")
        action_func = ACTION_FUNCTIONS.get(action)
        if action_func:
            action_func(param, raw_command=command)
        else:
            speak(f"Sorry, I don't understand the action '{action}'.")


def voice_command_ai_loop():
    """Main loop for listening to voice commands."""
    global last_command_time
    config = load_config()
    wake_word = config.get("wake_word", "jarvis").lower()
    wake_timeout = config.get("wake_timeout", 60)

    speak(f"{wake_word.capitalize()} voice assistant initialized and ready.")

    while True:
        # 🔁 Reload config every loop to pick up changes
        config = load_config()
        if wake_word != config.get("wake_word", "jarvis").lower():
            wake_word = config.get("wake_word", "jarvis").lower()
            print(f"[Voice] New Wake Word: {wake_word}")
        wake_timeout = config.get("wake_timeout", 60)

        command = listen_for_command()
        if not command:
            continue

        command_lower = command.strip().lower()

        if not state.jarvis_awake:
            if command_lower.startswith(wake_word):
                state.jarvis_awake = True
                last_command_time = time.time()
                command = command_lower[len(wake_word):].strip()
                if not command:
                    continue
            else:
                continue
        else:
            last_command_time = time.time()
            if command_lower.startswith(wake_word):
                command = command_lower[len(wake_word):].strip()
            else:
                command = command_lower

        process_command(command)

        if state.jarvis_awake and (time.time() - last_command_time > wake_timeout):
            state.jarvis_awake = False
            speak(f"Going to sleep. Say '{wake_word}' to wake me again.")
