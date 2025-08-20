# memory.py

history = []  # list of {"command": ..., "param": ...}

def store_interaction(command, param):
    """
    Store the full command heard and the GPT param output for context tracking.
    """
    history.append({
        "command": command,
        "param": param
    })

def get_last_interaction():
    """
    Return the last stored command and param as a dict.
    """
    if history:
        return history[-1]
    return None

def get_history():
    """
    Return the entire interaction history list.
    """
    return history

def clear_history():
    """
    Clear all stored history.
    """
    history.clear()

def get_formatted_history(max_items=5):
    """
    Return last N interactions formatted as a chat list for prompt context.
    Example output format:

    [
      {"role": "user", "content": "what is 2+2"},
      {"role": "assistant", "content": "2+2=4"},
      {"role": "user", "content": "can you explain that?"},
      {"role": "assistant", "content": "Sure! Adding 2 and 2 gives 4..."}
    ]
    """
    chat_history = []
    recent = history[-max_items:] if len(history) > max_items else history
    for i, entry in enumerate(recent):
        # user command
        chat_history.append({"role": "user", "content": entry["command"]})
        # assistant response
        chat_history.append({"role": "assistant", "content": entry["param"]})
    return chat_history
