import time
import threading
from playsound import playsound

# 🎵 Function to play the song in background
def playMusic():
    while True:  # repeat the song in a loop
        playsound('I wanna dance.mp3')

# 🎤 Function to print the lyrics line by line
def printLyrics():
    lines = [
        ("I wanna da-", 0.6),
        ("I wanna dance in the lights", 1.2),
        ("I wanna ro-", 0.7),
        ("I wanna rock that body", 1.0),
        ("I wanna go", 0.8),
        ("I wanna go for a ride", 1.2),
        ("Hop in the music and", 0.9),
        ("Rock your body", 0.8),
        ("Rock that body", 0.9),
        ("come on, come on", 0.7),
        ("Rock that body", 0.8),
        ("(Rock your body)", 0.6),
        ("Rock that body", 0.9),
        ("come on, come on", 0.7),
        ("Rock that body", 1.0)
    ]

    for text, delay in lines:
        for char in text:
            print(char, end="", flush=True)
            time.sleep(0.05)  # typing speed
        print()  # new line after each lyric
        time.sleep(delay)  # pause between lines

# 🎬 Start playing music and lyrics together
music_thread = threading.Thread(target=playMusic, daemon=True)
music_thread.start()

# Run the lyric animation
printLyrics()
