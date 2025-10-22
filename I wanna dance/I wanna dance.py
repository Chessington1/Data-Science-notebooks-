import time
import threading
import pygame

# 🎵 Function to play the music in background (looped)
def playMusic():
    pygame.mixer.init()
    pygame.mixer.music.load('rock_that_body.mp3')  # Your song file name
    pygame.mixer.music.play(-1)  # -1 = repeat forever

# 🎤 Function to print lyrics with typing animation
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
            time.sleep(0.05)  # typing speed per character
        print()  # new line
        time.sleep(delay)  # pause between lines

# 🎬 Start the music in a background thread
music_thread = threading.Thread(target=playMusic, daemon=True)
music_thread.start()

# 🎤 Run the lyric animation
printLyrics()

# Optional: Keep the program running so music continues
while True:
    time.sleep(1)

