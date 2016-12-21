#
# from gevent.wsgi import WSGIServer
# from multiprocessing import Process, Queue, Manager, Value
# from multiprocessing.queues import Empty
# import multiprocessing, logging
# from goprohero import GoProHero
# from threading import Thread, Event
# import time
# from RPi import GPIO
# import yaml
# from gevent import monkey
# import wifi
# from adapters import MockGPSAdapter, MockAngleAdapter
# import sys
# sys.path.append("/home/jeff/dev/blackbox-tryout")
# from shared.measurement import Measurement
# sys.path.append("/home/jeff/dev/blackbox-tryout/web")
# from app import create_app
#
#
# logger = multiprocessing.log_to_stderr(logging.WARN)
#
# class WebProcess(Process):
#     def __init__(self,sharedData, *args,**kwargs):
#         monkey.patch_all(socket=False,thread=False)
#         super(WebProcess, self).__init__(*args,**kwargs)
#         self.sharedData = sharedData
#
#     def run(self):
#         logger.info('fetching web app')
#
#         app = create_app(self.sharedData['flask'],self.sharedData)
#
#         # app.run('localhost',5123, False,threaded=True)
#         server = WSGIServer(('127.0.0.1', 5123), app)
#         try:
#             logger.info('serving app forever')
#             server.serve_forever()
#         except KeyboardInterrupt:
#             server.stop()
#
#         logger.info('Process Finished!')
#
#
# class WifiManagerProcess(Process):
#     def __init__(self,shared_data,changed_event,*args,**kwargs):
#         super(WifiManagerProcess, self).__init__(*args,**kwargs)
#         self.shared_data = shared_data
#         self.changed_event = changed_event
#
#     def run(self):
#         try:
#             while True:
#                 cell = wifi.Cell.where('wlan0',lambda c: c.ssid == 'Wifi Slort')
#                 scheme = wifi.Scheme.for_cell('wlan0','Wifi Slort',cell,'W59VDL43')
#                 scheme.activate()
#                 if not self.changed_event.is_set():
#                     self.changed_event.wait()
#
#
#
#         except (KeyboardInterrupt,SystemExit):
#             pass
#
#
# class StoppableThread(Thread):
#     def __init__(self,*args,**kwargs):
#         super(StoppableThread,self).__init__(*args,**kwargs)
#         self.running = False
#
#     def start(self):
#         self.running = True
#         super(StoppableThread,self).start()
#
#     def stop(self):
#         logger.info("Stopping thread {}".format(self))
#         self.running = False
#
#
# class MeasurementThread(StoppableThread):
#     def __init__(self,event,queue,sharedData, *args, **kwargs):
#         super(MeasurementThread, self).__init__(*args, **kwargs)
#         self.event = event
#         self.q = queue
#         self.sharedData = sharedData
#
#     def run(self):
#         gps_adapter = MockGPSAdapter()
#         pitch_adapter = MockAngleAdapter()
#
#         while self.running:
#             if not self.event.is_set():
#                 logger.log('Waiting for starting event')
#                 self.event.wait()
#
#             if not self.q.full():
#                 m = Measurement()
#                 gps_position = gps_adapter.get_current_gps()
#
#                 m.set_gps(gps_position)
#
#                 euler_angles = pitch_adapter.get_euler()
#
#                 m.set_euler(euler_angles)
#
#                 logger.debug("current measurment: {}".format(str(m)))
#                 self.q.put(m)
#                 self.sharedData['measurement'] = m.to_json()
#             # count +=1
#             time.sleep(1)
#
#
# class IoThread(StoppableThread):
#     def __init__(self,event, *args, **kwargs):
#         super(IoThread,self).__init__(*args,**kwargs)
#         self.event = event
#
#         GPIO.setup(18, GPIO.IN)
#
#     def run(self):
#         while self.running:
#             input = GPIO.input(18)
#             logger.debug('GPIO 18 input = {}'.format(input))
#             if not self.event.is_set() and input == 1:
#                 logger.info("Fire start event")
#                 self.event.set()
#             elif self.event.is_set() and input == 0:
#                 logger.info("Fire start event")
#                 self.event.clear()
#             time.sleep(1)
#
#         self.shutdown()
#
#     def shutdown(self):
#         if self.event.is_set():
#             self.event.clear()
#         try:
#             GPIO.cleanup(18)
#         except NotImplementedError:
#             pass
#
#
# class GoProThread(StoppableThread):
#     def __init__(self,event, *args, **kwargs):
#        super(GoProThread,self).__init__(*args,**kwargs)
#        self.event = event
#        self.recording = False
#        self.camera = GoProHero(password='password')
#
#     def start_recording(self):
#         if self.camera.command('record', 'on') is True:
#             logger.info("Started Recording")
#             self.recording = True
#
#     def stop_recording(self):
#         if self.camera.command('record', 'off') is True:
#             logger.info("Stopped Recording")
#             self.recording = False
#
#     def run(self):
#         while self.running:
#             if self.event.is_set() and self.recording is False:
#                 self.start_recording()
#             elif not self.event.is_set() and self.recording is True:
#                 self.stop_recording()
#
#         self.shutdown()
#
#     def shutdown(self):
#         if self.recording:
#             self.stop_recording()
#
#
# class WriterThread(StoppableThread):
#     def __init__(self,event,result_queue, *args, **kwargs):
#         super(WriterThread, self).__init__(*args, **kwargs)
#         self.event = event
#         self.result_queue = result_queue
#         self.current_file = self.generate_filename()
#
#     def run(self):
#         while self.running or not self.result_queue.empty():
#             try:
#                 measurement = self.result_queue.get(timeout=1)
#
#                 with open(self.get_current_file(), 'a') as f:
#                     logger.debug('writing measurement - {}'.format(measurement))
#                     f.write(str(measurement)+"\n")
#                 if self.result_queue.empty() and not self.event.is_set():
#                     logger.info('Rotating measurement file')
#                     self.finish()
#             except Empty:
#                 pass
#
#     def finish(self):
#         filename = self.generate_filename()
#         self.set_current_file(filename)
#
#     def generate_filename(self):
#         from datetime import datetime as dt
#
#         return  str(dt.now().strftime('%Y%m%d%H%M')) + "_results.csv"
#
#     def set_current_file(self,file):
#         self.current_file = file
#
#     def get_current_file(self):
#         return self.current_file
#
#
# class MeasurementProcess(Process):
#     def __init__(self,sharedData, *args,**kwargs):
#         super(MeasurementProcess, self).__init__(*args,**kwargs)
#
#         self.sharedData = sharedData
#
#     def run(self):
#         StartEvent = Event()
#         StartEvent.set()
#
#         measurmentQueue = Queue()
#
#         threads = [
#             # IoThread(StartEvent),
#             # GoProThread(StartEvent),
#             MeasurementThread(StartEvent, measurmentQueue, self.sharedData),
#             WriterThread(StartEvent,measurmentQueue)
#         ]
#         try:
#
#             for thread in threads:
#                 logger.info('starting thread {}'.format(thread))
#                 thread.start()
#
#             for thread in threads:
#                 thread.join()
#
#         except KeyboardInterrupt:
#             for thread in threads:
#                 thread.stop()
#                 thread.join()
#
#         logger.info('Process Finished!')
#
# def create_manager():
#
#     dataManager = Manager()
#     with open('config.yml') as f:
#         config = yaml.load(f)
#         sharedData = dataManager.dict(config)
#
#     return sharedData
#
# if __name__ == '__main__':
#
#
#     sharedData = create_manager()
#
#
#     processes = [
#         WebProcess(sharedData),
#         MeasurementProcess(sharedData)
#     ]
#     try:
#         for process in processes:
#             logger.info('Starting process {}'.format(process))
#             process.start()
#
#         for process in processes:
#             logger.info('Joining process {}'.format(process))
#             process.join()
#
#     except (KeyboardInterrupt, SystemExit):
#         logger.warning('Process interrupted')
#
#
