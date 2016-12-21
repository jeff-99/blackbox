from RPi import GPIO
from time import sleep

GPIO.setup(18, GPIO.IN)
GPIO.setup(17, GPIO.OUT)

running = True
input = 0
changed = 0
while running:
    previous_input = input
    input = GPIO.input(18)
    print(input)
    if(previous_input != input):
        changed += 1
        GPIO.output(17,input)
    if(changed > 5):
        break
    else:
        sleep(0.5)
