from speech_utils import speak, listen_for_command
from ai_parser import parse_command_with_ai
from actions import ACTION_FUNCTIONS
import time
import state

state.jarvis_awake = False
last_command_time = 0
WAKE_WORD = "jarvis"
WAKE_TIMEOUT = 60  # seconds



def voice_command_ai_loop():
    global last_command_time
    speak("Jarvis voice assistant initialized and ready.")

    while True:
        command = input()
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

        if state.jarvis_awake and (time.time() - last_command_time > WAKE_TIMEOUT):
            state.jarvis_awake = False
            speak("Going to sleep. Say 'Jarvis' to wake me again.")


if __name__ == "__main__":
    voice_command_ai_loop()