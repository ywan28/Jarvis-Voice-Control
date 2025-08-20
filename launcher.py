import threading
from gui import launch_config_gui
from voice_commands import voice_command_ai_loop  # your voice loop

def main():
    # Start the voice assistant in a separate thread
    voice_thread = threading.Thread(target=voice_command_ai_loop, daemon=True)
    voice_thread.start()

    # Start the GUI on the main thread
    launch_config_gui()

if __name__ == '__main__':
    main()
