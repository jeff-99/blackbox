import time
try:
    from RPi import GPIO
except (ImportError, RuntimeError):
    import sys
    sys.path.append("/home/jeff/dev/blackbox-tryout/compat")
    from CRPi import GPIO
from multiprocessing.util import get_logger

logger = get_logger()

def health_check(event) :
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)

    while event.is_set():
        GPIO.output(17, 1)
        time.sleep(1)
        GPIO.output(17,0)
        time.sleep(1)

    GPIO.cleanup()

