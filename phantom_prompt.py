import time
import random
import enchant
from pynput import keyboard

# Setup spell checker
d = enchant.Dict("en_US")

# Prompt pool
sentences = [
    "The slow loris climbs with patience.",
    "Typing fast is not the same as typing well.",
    "We are creatures of the night.",
    "Ghost trails reveal our hesitation.",
    "Every key tells a story."
]

# Global backspace counter
backspace_count = 0

# Capture backspaces during input
def count_backspaces():
    def on_press(key):
        global backspace_count
        if key == keyboard.Key.backspace:
            backspace_count += 1
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    return listener

def evaluate_prompt(target, typed):
    target_words = target.strip().split()
    typed_words = typed.strip().split()

    total_words = len(target_words)
    correct = 0
    mistyped_words = 0
    misspelled_words = 0

    for i in range(min(len(typed_words), total_words)):
        if typed_words[i] == target_words[i]:
            correct += 1
        else:
            mistyped_words += 1
            if not d.check(typed_words[i]):
                misspelled_words += 1

    extra_words = max(0, len(typed_words) - total_words)
    mistyped_words += extra_words
    for i in range(total_words, len(typed_words)):
        if not d.check(typed_words[i]):
            misspelled_words += 1

    accuracy = (correct / total_words) * 100 if total_words > 0 else 0
    return total_words, correct, mistyped_words, misspelled_words, accuracy

def calculate_wpm(typed_text, duration_secs):
    word_count = len(typed_text.strip().split())
    return (word_count / duration_secs) * 60 if duration_secs > 0 else 0

def main():
    global backspace_count
    prompt = random.choice(sentences)
    print("\nType the following sentence:")
    print(f"\n\033[92m{prompt}\033[0m")
    input("\nPress Enter when you're ready to begin...\n")

    backspace_count = 0
    listener = count_backspaces()

    start_time = time.time()
    typed = input("\n> ")
    end_time = time.time()
    listener.stop()

    duration = end_time - start_time
    wpm = calculate_wpm(typed, duration)

    total, correct, mistyped, misspelled, accuracy = evaluate_prompt(prompt, typed)

    print("\n--- Results ---")
    print(f"Time Taken:       {duration:.2f} seconds")
    print(f"WPM:              {wpm:.2f}")
    print(f"Accuracy:         {accuracy:.2f}%")
    print(f"Words Typed:      {len(typed.strip().split())}")
    print(f"Correct Words:    {correct}")
    print(f"Mistyped Words:   {mistyped}")
    print(f"Misspelled Words: {misspelled}")
    print(f"Backspaces:       {backspace_count}")
    print("-----------------\n")

if __name__ == "__main__":
    main()
