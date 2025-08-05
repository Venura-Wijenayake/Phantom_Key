from pynput import keyboard
import time
import threading
import os
import string
from collections import deque, defaultdict
from datetime import datetime
import enchant

# Spell check setup
spellchecker = enchant.Dict("en_US")

# Session stats
total_chars = 0
session_start = None
session_end = None
backspace_count = 0
misspelled_count = 0
keystroke_counter = defaultdict(float)

# Instant window stats
keystroke_times = deque()
backspace_times = deque()
ghost_chars = deque(maxlen=65)

window_seconds = 10
idle_threshold = 5
last_key_time = None
active = False
exit_flag = False
lock = threading.Lock()

# Word buffer for spell check
current_word = []

# Keystroke log tracking
keystroke_log = []
keystroke_logging_enabled = False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def log_session():
    global session_start, session_end
    try:
        start_str = datetime.fromtimestamp(session_start).strftime('%Y-%m-%d %H:%M')
        end_str = datetime.fromtimestamp(session_end).strftime('%H:%M')
        session_duration = session_end - session_start
        session_cps = total_chars / session_duration if session_duration > 0 else 0
        session_wpm = (total_chars / 5) / (session_duration / 60) if session_duration > 0 else 0
        weighted_errors = (backspace_count * 0.5 + misspelled_count * 1.5)
        session_mistake_rate = (weighted_errors / total_chars * 100) if total_chars > 0 else 0

        log_line = (
            f"[{start_str} → {end_str}] "
            f"WPM: {session_wpm:.2f} | CPS: {session_cps:.2f} | "
            f"Chars: {total_chars} | Backs: {backspace_count} | "
            f"Misspelled: {misspelled_count} | "
            f"Mistakes: {session_mistake_rate:.2f}%\n"
        )

        with open("phantom_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(log_line)

        if keystroke_logging_enabled:
            with open("phantom_keystrokes.txt", "w", encoding="utf-8") as kf:
                kf.write(''.join(keystroke_log))

        print("\nSession logged to phantom_log.txt")
        if keystroke_logging_enabled:
            print("Keystrokes saved to phantom_keystrokes.txt")

        if os.path.exists("phantom_stats.txt"):
            os.remove("phantom_stats.txt")

    except Exception as e:
        print(f"[Logging Error] {e}")

def write_initial_stats_file():
    try:
        with open("phantom_stats.txt", "w", encoding="utf-8") as f:
            f.write("0.00|0.00|0|0|0.00|0.00|0.00||0|Keystroke Log: OFF")
    except Exception as e:
        print(f"[Initial HUD File Error] {e}")

def write_heatmap_file():
    try:
        with open("phantom_heatmap.txt", "w", encoding="utf-8") as f:
            for key, count in keystroke_counter.items():
                if count > 0.1:
                    f.write(f"{key}:{count:.2f}\n")
    except Exception as e:
        print(f"[Heatmap Export Error] {e}")

def decay_keystrokes():
    for key in list(keystroke_counter.keys()):
        keystroke_counter[key] *= 0.95
        if keystroke_counter[key] < 0.1:
            del keystroke_counter[key]

def calculate_stats():
    global total_chars, session_start, last_key_time, backspace_count, misspelled_count, exit_flag
    while not exit_flag:
        time.sleep(1)
        with lock:
            now = time.time()

            while keystroke_times and now - keystroke_times[0] > window_seconds:
                keystroke_times.popleft()
            while backspace_times and now - backspace_times[0] > window_seconds:
                backspace_times.popleft()

            instant_elapsed = now - keystroke_times[0] if keystroke_times else 1
            instant_chars = len(keystroke_times)
            instant_backs = len(backspace_times)
            instant_cps = instant_chars / instant_elapsed if instant_elapsed > 0 else 0
            instant_wpm = (instant_chars / 5) / (instant_elapsed / 60) if instant_elapsed > 0 else 0
            instant_mistake_rate = ((instant_backs * 0.5) / instant_chars * 100) if instant_chars > 0 else 0

            if not keystroke_times or (now - keystroke_times[-1]) > idle_threshold:
                instant_wpm = 0
                instant_cps = 0
                instant_mistake_rate = 0

            if not session_start:
                continue
            session_elapsed = now - session_start
            session_cps = total_chars / session_elapsed if session_elapsed > 0 else 0
            session_wpm = (total_chars / 5) / (session_elapsed / 60) if session_elapsed > 0 else 0
            weighted_errors = (backspace_count * 0.5 + misspelled_count * 1.5)
            session_mistake_rate = (weighted_errors / total_chars * 100) if total_chars > 0 else 0

            clear_screen()
            print("Phantom_Key - Live Typing Stats")
            print("--------------------------------")
            print(f"Session WPM:       {session_wpm:.2f}")
            print(f"Session CPS:       {session_cps:.2f}")
            print(f"Total Chars:       {total_chars}")
            print(f"Backspaces:        {backspace_count}")
            print(f"Misspelled Words:  {misspelled_count}")
            print(f"Mistake Rate:      {session_mistake_rate:.2f}%")
            print("")
            print(f"Instant WPM:       {instant_wpm:.2f} (last {window_seconds}s)")
            print(f"Instant CPS:       {instant_cps:.2f}")
            print(f"Instant Mistakes:  {instant_mistake_rate:.2f}%")
            print(f"Idle Reset:        {'Yes' if instant_wpm == 0 else 'No'}")
            print(f"Keystroke Log:     {'ON' if keystroke_logging_enabled else 'OFF'}")
            print("")
            print("Press F6 to stop... | Press F5 to toggle log\n")

            try:
                with open("phantom_stats.txt", "w", encoding="utf-8") as f:
                    ghost_str = ''.join(ghost_chars)
                    log_status = "Keystroke Log: ON" if keystroke_logging_enabled else "Keystroke Log: OFF"
                    f.write(
                        f"{session_wpm:.2f}|{session_cps:.2f}|{total_chars}|"
                        f"{backspace_count}|{session_mistake_rate:.2f}|"
                        f"{instant_wpm:.2f}|{instant_cps:.2f}|{ghost_str}|{misspelled_count}|{log_status}"
                    )
            except Exception as e:
                print(f"[HUD Export Error] {e}")

            decay_keystrokes()
            write_heatmap_file()

def on_press(key):
    global total_chars, session_start, session_end, last_key_time, active
    global backspace_count, exit_flag, current_word, misspelled_count, keystroke_logging_enabled

    now = time.time()

    if key == keyboard.Key.f6:
        with lock:
            session_end = time.time()
            exit_flag = True
            log_session()
        return False

    if key == keyboard.Key.f5:
        with lock:
            keystroke_logging_enabled = not keystroke_logging_enabled
        return

    try:
        key_label = None
        char_to_log = ''

        if hasattr(key, 'char') and key.char is not None and key.char.isprintable():
            key_label = key.char
            char_to_log = key.char
            with lock:
                if not active:
                    session_start = now
                    active = True
                total_chars += 1
                last_key_time = now
                keystroke_times.append(now)
                ghost_chars.append(key.char)
                current_word.append(key.char)

        elif key in [keyboard.Key.space, keyboard.Key.enter]:
            key_label = 'space' if key == keyboard.Key.space else 'enter'
            char_to_log = '\n' if key == keyboard.Key.enter else ' '
            with lock:
                if current_word:
                    word = ''.join(current_word).strip()
                    cleaned_word = word.strip(string.punctuation)
                    if cleaned_word and not spellchecker.check(cleaned_word):
                        misspelled_count += 1
                    current_word.clear()
                total_chars += 1
                last_key_time = now
                keystroke_times.append(now)
                ghost_chars.append('↵' if key == keyboard.Key.enter else ' ')

        elif key == keyboard.Key.backspace:
            key_label = 'backspace'
            char_to_log = '[BS]'
            with lock:
                backspace_count += 1
                backspace_times.append(now)
                if current_word:
                    current_word.pop()
                ghost_chars.append('⌫')

        elif key == keyboard.Key.left:
            key_label = 'left'
            char_to_log = '[←]'
            with lock:
                ghost_chars.append('←')
        elif key == keyboard.Key.right:
            key_label = 'right'
            char_to_log = '[→]'
            with lock:
                ghost_chars.append('→')
        elif key == keyboard.Key.up:
            key_label = 'up'
            char_to_log = '[↑]'
            with lock:
                ghost_chars.append('↑')
        elif key == keyboard.Key.down:
            key_label = 'down'
            char_to_log = '[↓]'
            with lock:
                ghost_chars.append('↓')

        if key_label:
            with lock:
                keystroke_counter[key_label] += 1.0
                if keystroke_logging_enabled and char_to_log:
                    keystroke_log.append(char_to_log)

    except:
        pass

def main():
    write_initial_stats_file()
    stat_thread = threading.Thread(target=calculate_stats, daemon=True)
    stat_thread.start()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
