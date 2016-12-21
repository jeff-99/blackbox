
from multiprocessing.queues import Empty
from .goprohero import GoProHero
from .message import Message
from threading import Thread
import time
import sys
from datetime import datetime as dt
import os,csv

try:
    from RPi import GPIO
except (ImportError, RuntimeError):
    sys.path.append("/home/jeff/dev/blackbox-tryout/compat")
    from CRPi import GPIO

from .adapters import get_adapter_class
from .measurement import Measurement

from multiprocessing.util import get_logger

logger = get_logger()


class StoppableThread(Thread):
    def __init__(self,*args,**kwargs):
        super(StoppableThread,self).__init__(*args,**kwargs)
        self.running = False

    def start(self):
        self.running = True
        super(StoppableThread,self).start()

    def stop(self):
        logger.info("Stopping thread {}".format(self))
        self.running = False


class MeasurementThread(StoppableThread):
    def __init__(self,event,queue,sharedData, *args, **kwargs):
        super(MeasurementThread, self).__init__(*args, **kwargs)
        self.event = event
        self.q = queue
        self.sharedData = sharedData

    def run(self):
        gps_adapter = get_adapter_class(self.sharedData['measurement']['adapters']['gps'])()
        orientation_adapter = get_adapter_class(self.sharedData['measurement']['adapters']['orientation'])()
        logger.warn(type(orientation_adapter))

        add_delay = False
        while self.running:
            if not self.event.is_set():
                logger.debug('Waiting for starting event')
                self.event.wait(0.01)
                add_delay = True
                continue

            if add_delay:
                # gopro recording delay
                time.sleep(0.75)
                add_delay = False

            if not self.q.full():
                # m_start = time.time()
                m = Measurement()
                gps_position = gps_adapter.get_current_gps()
                # logger.info("measured speed = {}".format(gps_position.get_kmh()))
                m.set_gps(gps_position)

                pitch = orientation_adapter.get_pitch()
                m.set_angle(pitch)

                acceleration = orientation_adapter.get_acceleration()
                m.set_acceleration(acceleration)

                temperature = orientation_adapter.get_temperature()
                m.set_temperature(temperature)

                # logger.debug("current measurment: {}".format(str(m)))
                msg = Message(type="measurement", payload=m.to_json())
                self.q.put(msg)
                self.sharedData['measurement'] = m.to_json()

                # m_end = time.time()
                # logger.info("measurement time = {}".format(m_end-m_start))
            time.sleep(0.1)


class IoThread(StoppableThread):
    def __init__(self,event, *args, **kwargs):
        super(IoThread,self).__init__(*args,**kwargs)
        self.event = event

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(27, GPIO.OUT)

    def run(self):
        try:
            led_is_on = False
            while self.running:
                input = GPIO.input(25)
                logger.debug("Pin 25 input = {}".format(input))
                if input and not led_is_on:
                    logger.debug("turn on led 27")
                    GPIO.output(27,1)
                    led_is_on = True
                elif input == 0 and led_is_on:
                    logger.debug("turn off led 27")
                    GPIO.output(27,0)
                    led_is_on = False
                # logger.debug('GPIO 18 input = {}'.format(input))
                if not self.event.is_set() and input == 1:
                    logger.debug("Fire start event")
                    self.event.set()
                elif self.event.is_set() and input == 0:
                    logger.debug("Fire stop event")
                    self.event.clear()
                time.sleep(0.1)

            self.shutdown()
        except (SystemExit, KeyboardInterrupt):
            GPIO.cleanup()

    def shutdown(self):
        if self.event.is_set():
            self.event.clear()
        try:
            GPIO.cleanup()
        except NotImplementedError:
            pass


class GoProThread(StoppableThread):
    def __init__(self,event,queue, gopro_config, *args, **kwargs):
       super(GoProThread,self).__init__(*args,**kwargs)
       self.event = event
       self.queue = queue
       self.recording = False
       self.camera = GoProHero(ip=gopro_config['host'], password=gopro_config['password'])

    def start_recording(self):
        if self.camera.command('record', 'on') is True:
            self.queue.put(Message(type="status", payload={"name" : "gopro", "message": "started_recording" , "timestamp": time.time()}))
            logger.info("Started Recording")
            self.recording = True

    def stop_recording(self):
        if self.camera.command('record', 'off') is True:
            self.queue.put(Message(type="status", payload={"name" : "gopro", "message": "stopped_recording" , "timestamp": time.time()}))
            logger.info("Stopped Recording")
            self.recording = False

    def run(self):
        while self.running:
            if self.event.is_set() and self.recording is False:
                self.start_recording()
            elif not self.event.is_set() and self.recording is True:
                self.stop_recording()
            time.sleep(0.01)

        self.shutdown()

    def shutdown(self):
        if self.recording:
            self.stop_recording()


class WriterThread(StoppableThread):
    def __init__(self,event,result_queue,output_dir, file_format, *args, **kwargs):
        super(WriterThread, self).__init__(*args, **kwargs)
        self.event = event
        self.result_queue = result_queue
        self.output_dir = output_dir
        self.file_format = file_format
        self.current_file = self.generate_filename()

    def run(self):
        while self.running or not self.result_queue.empty():
            try:
                message = self.result_queue.get(timeout=1)
                logger.debug(message.type)
                if not isinstance(message, Message):
                    continue

                if message.type == 'measurement':
                    measurement = Measurement.from_json(message.payload)
                    with open(self.get_current_file(), 'a') as f:
                        logger.debug('writing measurement - {}'.format(measurement))
                        # f.write(str(measurement)+"\n")
                        writer = csv.writer(f,delimiter=',')
                        writer.writerow(measurement.to_tuple())
                elif message.type == 'status':
                    data = message.payload
                    with open(os.path.join(self.output_dir,"status.log"), 'a') as status_file:
                        writer = csv.DictWriter(status_file,["name", "message", "timestamp"])
                        writer.writerow(data)

            except Empty:
                if not self.event.is_set():
                    logger.debug('Rotating measurement file')
                    self.finish()

    def finish(self):
        filename = self.generate_filename()
        self.set_current_file(filename)

    def generate_filename(self):
        return os.path.join(self.output_dir,self.file_format.format(str(dt.now().strftime('%Y%m%d%H%M%S'))))

    def set_current_file(self,file):
        self.current_file = file

    def get_current_file(self):
        return self.current_file