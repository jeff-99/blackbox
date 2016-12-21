from gevent.wsgi import WSGIServer
from multiprocessing import Process, Event, Queue
from .thread import MeasurementThread, IoThread, GoProThread, WriterThread
from gevent import monkey
import sys

from app import create_app
from multiprocessing.util import get_logger

logger = get_logger()


class WebProcess(Process):
    def __init__(self,sharedData, *args,**kwargs):
        monkey.patch_all(socket=False,thread=False)
        super(WebProcess, self).__init__(*args,**kwargs)
        self.sharedData = sharedData

    def run(self):
        logger.info('fetching web app')

        app = create_app(self.sharedData['flask'],self.sharedData)

        # app.run('localhost',5123, False,threaded=True)
        server = WSGIServer((self.sharedData['wsgi']['host'], self.sharedData['wsgi']['port']), app)
        try:
            logger.info('serving app forever')
            server.serve_forever()
        except KeyboardInterrupt:
            server.stop()

        logger.info('Process Finished!')


class MeasurementProcess(Process):
    def __init__(self,sharedData, *args,**kwargs):
        super(MeasurementProcess, self).__init__(*args,**kwargs)

        self.sharedData = sharedData

    def run(self):
        StartEvent = Event()

        measurement_queue = Queue()

        threads = [
            IoThread(StartEvent),
            GoProThread(StartEvent,measurement_queue,self.sharedData['gopro']),
            MeasurementThread(StartEvent, measurement_queue, self.sharedData),
            WriterThread(StartEvent,measurement_queue,self.sharedData['output']['basepath'], self.sharedData['output']['format'])
        ]
        try:
            for thread in threads:
                logger.info('starting thread {}'.format(thread))
                thread.start()

            for thread in threads:
                thread.join()

        except (SystemExit,KeyboardInterrupt):
            for thread in threads:
                thread.stop()
                thread.join()

        logger.info('Measurement Process Finished!')