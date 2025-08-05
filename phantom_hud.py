import tkinter as tk
import time
import threading
import os
import sys
import keyboard  # Hotkey listener

# Global toggle
heatmap_visible = True
status_message = "Keystroke Log: OFF"

# Color thresholds for typing speed (HUD)
def get_typing_color(wpm):
    if wpm == 0:
        return "gray40"
    elif wpm < 20:
        return "white"
    elif wpm < 40:
        return "yellow"
    elif wpm < 60:
        return "green"
    else:
        return "lime"

# Updated heat color gradient (blue → green → yellow → orange → red)
def get_heat_color(count):
    if count < 1:
        return "gray20"
    elif count < 5:
        return "steelblue"
    elif count < 15:
        return "green3"
    elif count < 30:
        return "gold"
    elif count < 50:
        return "orange"
    elif count < 80:
        return "red"
    else:
        return "firebrick"

# Final keyboard layout with special key spacing and arrow placement
keyboard_rows = [
    ['1','2','3','4','5','6','7','8','9','0','-','=','backspace'],
    ['q','w','e','r','t','y','u','i','o','p','[',']','\\'],
    ['a','s','d','f','g','h','j','k','l',';','\'','enter','up'],
    ['z','x','c','v','b','n','m',',','.','/', '',  'left', 'down', 'right'],
    ['', '', '', 'space', 'space', 'space', 'space', 'space', '', '', '', ''],
]

anchor_positions = ["top-left", "top-right", "bottom-right", "bottom-left"]
anchor_index = 0

def apply_anchor(root):
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    w, h = 700, 250
    pos = anchor_positions[anchor_index]
    if pos == "top-left":
        x, y = 30, 30
    elif pos == "top-right":
        x, y = sw - w - 30, 30
    elif pos == "bottom-right":
        x, y = sw - w - 30, sh - h - 60
    elif pos == "bottom-left":
        x, y = 30, sh - h - 60
    else:
        x, y = 30, 30
    root.geometry(f"{w}x{h}+{x}+{y}")

def draw_heatmap(canvas, counts, status_message):
    global heatmap_visible
    canvas.delete("all")
    if not heatmap_visible:
        return

    key_size = 25
    gap = 4
    start_x = 10
    start_y = 5

    canvas.create_text(690, 10, text=status_message, anchor='ne', fill="gray70", font=("Consolas", 10))

    for row_index, row in enumerate(keyboard_rows):
        for col_index, key in enumerate(row):
            if not key.strip():
                continue
            count = counts.get(key, 0)
            color = get_heat_color(count)
            x = start_x + col_index * (key_size + gap)
            y = start_y + row_index * (key_size + gap)
            canvas.create_rectangle(x, y, x + key_size, y + key_size, fill=color, outline="black")

            label_map = {
                'space': '␣',
                'enter': '↵',
                'backspace': '⌫',
                'up': '↑',
                'down': '↓',
                'left': '←',
                'right': '→'
            }
            label = label_map.get(key, key.upper() if len(key) == 1 else (key[0].upper() if key else ''))
            canvas.create_text(x + key_size/2, y + key_size/2, text=label, font=("Consolas", 9), fill="black")

def read_heatmap_counts():
    counts = {}
    if not os.path.exists("phantom_heatmap.txt"):
        return counts
    try:
        with open("phantom_heatmap.txt", "r", encoding="utf-8") as f:
            for line in f:
                if ':' in line:
                    key, val = line.strip().split(":")
                    counts[key] = float(val)
    except:
        pass
    return counts

def update_loop(label, canvas, root):


    def loop():
        global flash_timer, last_active_time, visible, status_message
        last_backspace_count = -1  # ✅ moved here
        flash_timer = 0
        last_active_time = time.time()
        visible = True

        while True:
            time.sleep(0.2)

            if not os.path.exists("phantom_stats.txt"):
                label.config(text="[HUD Notice]: phantom_stats.txt not found. Exiting...")
                root.after(1500, root.destroy)
                break

            with open("phantom_stats.txt", "r", encoding="utf-8") as f:
                raw = f.read().strip()
                if not raw:
                    label.config(text="[HUD Notice]: phantom_stats.txt is empty. Exiting...")
                    root.after(1500, root.destroy)
                    break

                data = raw.split("|")
                if len(data) >= 10:
                    session_wpm = float(data[0])
                    session_cps = float(data[1])
                    total_chars = int(data[2])
                    backspaces = int(data[3])
                    mistake_rate = float(data[4])
                    instant_wpm = float(data[5])
                    instant_cps = float(data[6])
                    ghost = data[7]
                    misspelled = int(data[8])
                    status_message = data[9]
                    idle = instant_wpm == 0

                    if not idle:
                        last_active_time = time.time()
                        if not visible:
                            root.deiconify()
                            visible = True

                    if backspaces > last_backspace_count:
                        flash_timer = 5
                    last_backspace_count = backspaces

                    text_color = "red" if flash_timer > 0 else get_typing_color(instant_wpm)
                    if flash_timer > 0:
                        flash_timer -= 1

                    if time.time() - last_active_time > 15:
                        if visible:
                            root.withdraw()
                            visible = False
                        continue

                    line1 = (
                        f"Session:  WPM {session_wpm:5.2f} | CPS {session_cps:4.2f} | "
                        f"Chars {total_chars:<4} | Backs {backspaces:<3} | Missp {misspelled:<2} | "
                        f"Mistakes {mistake_rate:5.2f}%"
                    )
                    line2 = (
                        f"Instant:  WPM {instant_wpm:5.2f} | CPS {instant_cps:4.2f} | "
                        f"Mistakes {0.00 if instant_cps == 0 else mistake_rate:5.2f}%"
                    )
                    line3 = f"Ghost:    {ghost[-90:]}"

                    label.config(text=f"{line1}\n{line2}\n{line3}", fg=text_color)

                    counts = read_heatmap_counts()
                    draw_heatmap(canvas, counts, status_message)

    threading.Thread(target=loop, daemon=True).start()

def setup_hotkeys(root):
    global anchor_index, heatmap_visible

    def on_f6():
        root.destroy()

    def on_f7():
        global anchor_index
        anchor_index = (anchor_index + 1) % len(anchor_positions)
        apply_anchor(root)

    def on_f8():
        if root.state() == "withdrawn":
            root.deiconify()
        else:
            root.withdraw()

    def on_f4():
        global heatmap_visible
        heatmap_visible = not heatmap_visible

    keyboard.add_hotkey("F6", on_f6)
    keyboard.add_hotkey("F7", on_f7)
    keyboard.add_hotkey("F8", on_f8)
    keyboard.add_hotkey("F4", on_f4)

def create_hud():
    global anchor_index
    root = tk.Tk()
    root.title("Phantom_Key HUD")
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.configure(bg='black')
    root.attributes("-alpha", 0.88)

    label = tk.Label(
        root,
        text="Waiting for Phantom_Key...",
        font=("Consolas", 10),
        fg="white",
        bg="black",
        justify='left',
        anchor='w'
    )
    label.pack(padx=0, pady=0)

    canvas = tk.Canvas(root, width=700, height=250, bg="black", highlightthickness=0)
    canvas.pack(pady=(0, 4))

    apply_anchor(root)
    update_loop(label, canvas, root)
    setup_hotkeys(root)
    root.mainloop()

if __name__ == "__main__":
    create_hud()
