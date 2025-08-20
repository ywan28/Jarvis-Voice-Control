# gui.py
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext
from config_manager import load_config, save_config
import pyttsx3
from voice_commands import process_command  # NEW

# ---------- Helpers ----------
def get_available_voices():
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        return [(i, v.name or f"Voice {i}") for i, v in enumerate(voices)]
    except Exception as e:
        messagebox.showwarning("Voices Unavailable", f"Could not load system voices:\n{e}")
        return [(0, "Default")]

def parse_csv_multiline(text_widget):
    raw = text_widget.get("1.0", tk.END)
    items = [x.strip() for x in raw.replace("\n", ",").split(",")]
    return [x for x in items if x]

def safe_int(value, default):
    try:
        return int(str(value).strip())
    except Exception:
        return default

def safe_float(value, default):
    try:
        return float(str(value).strip())
    except Exception:
        return default

class CollapsibleSection(ttk.Frame):
    def __init__(self, master, title="Section", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self._open = tk.BooleanVar(value=True)
        self._title_text = title
        self._title_var = tk.StringVar()
        self._refresh_title()

        self.header = ttk.Frame(self)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.columnconfigure(0, weight=1)

        self.toggle_btn = ttk.Button(
            self.header,
            textvariable=self._title_var,
            command=self.toggle,
            takefocus=False
        )
        self.toggle_btn.grid(row=0, column=0, sticky="w")

        self.body = ttk.Frame(self)
        self.body.grid(row=1, column=0, sticky="nsew")

    def _refresh_title(self):
        prefix = "▾ " if self._open.get() else "▸ "
        self._title_var.set(prefix + self._title_text)

    def toggle(self):
        self._open.set(not self._open.get())
        if self._open.get():
            self.body.grid(row=1, column=0, sticky="nsew")
        else:
            self.body.grid_remove()
        self._refresh_title()

class ConsoleTee:
    def __init__(self, orig_stream, text_widget: scrolledtext.ScrolledText):
        self.orig = orig_stream
        self.text = text_widget

    def write(self, message):
        try:
            self.orig.write(message)
        except Exception:
            pass

        def _append():
            try:
                self.text.configure(state=tk.NORMAL)
                self.text.insert(tk.END, message)
                self.text.see(tk.END)
                self.text.configure(state=tk.DISABLED)
            except Exception:
                pass

        try:
            self.text.after(0, _append)
        except Exception:
            pass

    def flush(self):
        try:
            self.orig.flush()
        except Exception:
            pass

# ---------- Main GUI ----------
def save_changes(entries, voice_idx_var, tts_speed_var):
    wake_word = entries["wake_word"].get().strip()
    if not wake_word:
        messagebox.showerror("Invalid Input", "Wake Word cannot be empty.")
        return

    wake_timeout = safe_int(entries["wake_timeout"].get(), None)
    if wake_timeout is None or wake_timeout < 0:
        messagebox.showerror("Invalid Input", "Wake Timeout must be a non-negative integer.")
        return

    voice_idx = safe_int(voice_idx_var.get(), 0)
    tts_speed = safe_float(tts_speed_var.get(), 200.0)

    config = {
        "wake_word": wake_word,
        "wake_timeout": wake_timeout,
        "voice": voice_idx,
        "tts_speed": tts_speed,
        "default_location": entries["default_location"].get().strip(),
        "default_stocks": parse_csv_multiline(entries["default_stocks"]),
        "default_news_topics": parse_csv_multiline(entries["default_news_topics"]),
        "openai_api_key": entries["openai_api_key"].get().strip(),
        "openweather_api_key": entries["openweather_api_key"].get().strip(),
    }

    try:
        save_config(config)
    except Exception as e:
        messagebox.showerror("Save Failed", f"Could not save configuration:\n{e}")
        return

    messagebox.showinfo("Saved", "Configuration saved successfully.")
    print("[GUI] Configuration saved:", config)

def launch_config_gui():
    config = load_config()
    root = tk.Tk()
    root.title("Jarvis Configuration")
    root.minsize(700, 650)
    ttk.Style(root)

    paned = ttk.Panedwindow(root, orient=tk.VERTICAL)
    paned.pack(fill="both", expand=True)
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    container = ttk.Frame(paned, padding=12)
    container.columnconfigure(1, weight=1)
    paned.add(container, weight=3)

    # --- Core Settings ---
    ttk.Label(container, text="Wake Word:").grid(row=0, column=0, sticky="w", pady=(0, 6))
    wake_entry = ttk.Entry(container)
    wake_entry.insert(0, config.get("wake_word", "hey jarvis"))
    wake_entry.grid(row=0, column=1, sticky="ew", pady=(0, 6))

    ttk.Label(container, text="Wake Timeout (seconds):").grid(row=1, column=0, sticky="w", pady=6)
    timeout_entry = ttk.Entry(container)
    timeout_entry.insert(0, str(config.get("wake_timeout", 3)))
    timeout_entry.grid(row=1, column=1, sticky="ew", pady=6)

    # Voice selection
    ttk.Label(container, text="Voice:").grid(row=2, column=0, sticky="w", pady=6)
    voices = get_available_voices()
    voice_values = [f"{i} - {name}" for i, name in voices]
    voice_idx_var = tk.IntVar(value=safe_int(config.get("voice", 0), 0))
    voice_display_var = tk.StringVar()

    def sync_voice_display_from_idx(*_):
        idx = voice_idx_var.get()
        if 0 <= idx < len(voices):
            voice_display_var.set(f"{idx} - {voices[idx][1]}")
        else:
            voice_idx_var.set(0)
            voice_display_var.set(f"0 - {voices[0][1]}")

    def on_voice_pick(event=None):
        raw = voice_combo.get()
        try:
            picked_idx = int(raw.split(" - ", 1)[0])
        except Exception:
            picked_idx = 0
        voice_idx_var.set(picked_idx)
        sync_voice_display_from_idx()
        print(f"[GUI] Voice selected: {voice_combo.get()}")

    sync_voice_display_from_idx()
    voice_combo = ttk.Combobox(
        container,
        textvariable=voice_display_var,
        values=voice_values,
        state="readonly",
        height=12
    )
    voice_combo.bind("<<ComboboxSelected>>", on_voice_pick)
    voice_combo.config(width=40, takefocus=True)
    voice_combo.grid(row=2, column=1, sticky="ew", pady=6)
    voice_combo.focus_set()

    # TTS speed slider
    ttk.Label(container, text="TTS Speed:").grid(row=3, column=0, sticky="w", pady=6)
    tts_speed_var = tk.DoubleVar(value=safe_float(config.get("tts_speed", 200), 200))
    tts_slider = ttk.Scale(container, from_=100, to=300, orient="horizontal", variable=tts_speed_var)
    tts_slider.grid(row=3, column=1, sticky="ew", pady=6)

    # --- Collapsible Personalizable Information ---
    personal = CollapsibleSection(container, title="Personalizable Information")
    personal.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 6))
    pf = personal.body
    pf.columnconfigure(1, weight=1)

    ttk.Label(pf, text="Default Location:").grid(row=0, column=0, sticky="w", pady=4)
    location_entry = ttk.Entry(pf)
    location_entry.insert(0, config.get("default_location", "New York, NY"))
    location_entry.grid(row=0, column=1, sticky="ew", pady=4)

    ttk.Label(pf, text="Default Stocks (comma/newline separated):").grid(row=1, column=0, sticky="nw", pady=4)
    stock_text = tk.Text(pf, height=3, width=40)
    stock_text.insert(tk.END, ", ".join(config.get("default_stocks", [])))
    stock_text.grid(row=1, column=1, sticky="ew", pady=4)

    ttk.Label(pf, text="Default News Topics (comma/newline separated):").grid(row=2, column=0, sticky="nw", pady=4)
    news_text = tk.Text(pf, height=3, width=40)
    news_text.insert(tk.END, ", ".join(config.get("default_news_topics", [])))
    news_text.grid(row=2, column=1, sticky="ew", pady=4)

    # --- Collapsible API Keys Section ---
    api_section = CollapsibleSection(container, title="API Keys")
    api_section.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 6))
    af = api_section.body
    af.columnconfigure(1, weight=1)

    ttk.Label(af, text="OpenAI API Key:").grid(row=0, column=0, sticky="w", pady=4)
    openai_entry = ttk.Entry(af, show="*")
    openai_entry.insert(0, config.get("openai_api_key", ""))
    openai_entry.grid(row=0, column=1, sticky="ew", pady=4)

    ttk.Label(af, text="OpenWeather API Key:").grid(row=1, column=0, sticky="w", pady=4)
    weather_entry = ttk.Entry(af, show="*")
    weather_entry.insert(0, config.get("openweather_api_key", ""))
    weather_entry.grid(row=1, column=1, sticky="ew", pady=4)

    # --- Text Command Input ---
    ttk.Label(container, text="Type Command:").grid(row=6, column=0, sticky="w", pady=6)
    command_entry = ttk.Entry(container)
    command_entry.grid(row=6, column=1, sticky="ew", pady=6)

    def send_typed_command(event=None):
        cmd = command_entry.get().strip()
        if cmd:
            process_command(cmd)
            command_entry.delete(0, tk.END)

    command_entry.bind("<Return>", send_typed_command)

    # --- Collect entries ---
    entries = {
        "wake_word": wake_entry,
        "wake_timeout": timeout_entry,
        "default_location": location_entry,
        "default_stocks": stock_text,
        "default_news_topics": news_text,
        "openai_api_key": openai_entry,
        "openweather_api_key": weather_entry,
    }

    # --- Collapsible Console Output Panel ---
    console_section = CollapsibleSection(paned, title="Console Output")
    paned.add(console_section, weight=1)
    console_section.body.rowconfigure(0, weight=1)
    console_section.body.columnconfigure(0, weight=1)

    console_text = scrolledtext.ScrolledText(
        console_section.body,
        height=10,
        wrap="word",
        state=tk.DISABLED
    )
    console_text.grid(row=0, column=0, sticky="nsew")

    # Duplicate stdout/stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = ConsoleTee(original_stdout, console_text)
    sys.stderr = ConsoleTee(original_stderr, console_text)

    print("[GUI] Console panel initialized. Output will appear here and in the terminal.")

    # --- Save Button ---
    save_btn = ttk.Button(
        container,
        text="Save Changes",
        command=lambda: save_changes(entries, voice_idx_var, tts_speed_var)
    )
    save_btn.grid(row=7, column=0, columnspan=2, pady=12)

    for col in (0, 1):
        container.columnconfigure(col, weight=1)

    def on_close():
        try:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        except Exception:
            pass
        root.withdraw()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
