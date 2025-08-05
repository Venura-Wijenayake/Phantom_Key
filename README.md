# Phantom_Key 🦥⌨️

Phantom_Key is a prototype keystroke overlay tool built in Python.  
It runs in the background while you type and displays:

- 📈 Words Per Minute (WPM), Characters Per Second (CPS)
- ⌫ Backspaces, misspellings, mistake rate
- 👻 A ghost trail of your recent typed characters
- 🔥 A real-time keystroke heatmap
- 📝 Optional session keystroke logging (F5 toggle)

---

## 🎮 Controls

| Key      | Action                             |
|----------|------------------------------------|
| `F4`     | Toggle heatmap on/off              |
| `F5`     | Toggle keystroke logging (on/off)  |
| `F6`     | Exit program cleanly               |
| `F7`     | Change HUD anchor position         |
| `F8`     | Hide/show HUD window               |

---

## 📂 Files

- `phantom_key.py` — main tracker
- `phantom_hud.py` — floating HUD + heatmap display
- `phantom_stats.txt` — live metrics file
- `phantom_keystrokes.txt` — optional keystroke log (when enabled)
- `phantom_heatmap.txt` — heat decay data for heatmap

---

## 🔮 Notes

- Best run in a local dev environment on Windows
- Currently a Python prototype (C# version planned)
- ⚠️ Note: The current heatmap may occasionally miss fast keystrokes due to event timing delays in Python. This will be addressed in a future version.
- Built by [@Venura-Wijenayake](https://github.com/Venura-Wijenayake)

> _“We are Slow Loris. We are creatures of the night. We Branch.”_

---

## 🧪 License

MIT License — you are free to fork, modify, and build on this.

---

Let me know if you want help uploading it, styling the repo page, or making a banner/logo. Want to add animated screenshots or a demo gif too?
