from time import sleep

import winsound


def beep(num: int = 1):
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 500  # Set Duration To 1000 ms == 1 second
    for i in range(num):
        sleep(.1)
        winsound.Beep(frequency, duration)


def message_beep():
    winsound.MessageBeep()
