from openai import OpenAI
import json
import memory
from ai_prompt import build_ai_prompt
from config_manager import load_config

# Load OpenAI API key from config
config = load_config()
OPENAI_API_KEY = config.get("openai_api_key", "")

client = OpenAI(api_key=OPENAI_API_KEY)

def parse_command_with_ai(command_text):
    memory_history = memory.get_formatted_history()
    base_prompt = build_ai_prompt(command_text)

    try:
        messages = [{"role": "system", "content": base_prompt}]
        messages.extend(memory_history)
        messages.append({"role": "user", "content": command_text})

        if not OPENAI_API_KEY:
            print("[AI] Missing OpenAI API key.")
            return {"action": "search", "param": command_text}

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        raw_text = response.choices[0].message.content.strip()
        print(f"[AI] Raw response: {raw_text}")
        parsed = json.loads(raw_text)
        return parsed
    except Exception as e:
        print(f"[AI] Parsing failed: {e}")
        return {"action": "search", "param": command_text}
