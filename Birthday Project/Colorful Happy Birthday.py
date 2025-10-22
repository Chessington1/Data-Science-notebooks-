import time
import threading
from random import randint
from playsound import playsound

def play_music():
    playsound('happy_birthday.mp3')  # Your renamed music file

def animation():
    for i in range(1, 85):
        print('')  # Adds blank lines for spacing

    space = ''
    for i in range(1, 1000):
        count = randint(1, 100)
        space = ' ' * count

        if i % 10 == 0:
            print(space + '🎂 Happy Birthday!')
        elif i % 9 == 0:
            print(space + '🎉')
        elif i % 5 == 0:
            print(space + '💛')
        elif i % 8 == 0:
            print(space + '🍕')
        elif i % 7 == 0:
            print(space + '🍫')
        elif i % 6 == 0:
            print(space + 'Happy Birthday! 💖')
        else:
            print(space + '🔶')

        time.sleep(0.2)

while True:
    # Start the song and animation together
    music_thread = threading.Thread(target=play_music)
    music_thread.start()

    animation()

    print("\n🎶 Replaying... 🎶\n")
    time.sleep(2)  # Short pause before looping

