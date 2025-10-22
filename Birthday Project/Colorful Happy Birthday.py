# 🎉 Colorful Happy Birthday with Real Music
from playsound import playsound
import threading
import time
from random import randint
def play_music():
    playsound('happy_birthday.mp3')
    thread = threading.Thread(target=play_music)
    thread.start()
    
name = "Emmanuel"

colors = [
    "\033[91m", "\033[92m", "\033[93m",
    "\033[94m", "\033[95m", "\033[96m", "\033[97m"
]
reset = "\033[0m"

# Play background music in a separate thread
def play_music():
    playsound("happy_birthday.mp3")  # Put your song file in the same folder

thread = threading.Thread(target=play_music)
thread.start()

for i in range(1, 85):
    print('')

space = ''
for i in range(1, 1000):
    count = randint(1, 100)
    while count > 0:
        space += ' '
        count -= 1

    color = colors[randint(0, len(colors) - 1)]

    if i % 10 == 0:
        print(space + color + f'🎂 Happy Birthday, {name}! 🎉' + reset)
    elif i % 9 == 0:
        print(space + color + '🎂' + reset)
    elif i % 5 == 0:
        print(space + color + '💛' + reset)
    elif i % 8 == 0:
        print(space + color + '🍕' + reset)
    elif i % 7 == 0:
        print(space + color + '🍫' + reset)
    elif i % 6 == 0:
        print(space + color + f'Happy Birthday, {name}! 💖' + reset)
    else:
        print(space + color + '💎' + reset)

    time.sleep(0.25)
    space = ''

