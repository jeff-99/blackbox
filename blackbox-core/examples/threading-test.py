from threading import Thread
from flask import Flask, Response
import time
from multiprocessing import Process


class WebThread(Thread):
    def run(self):
        self.app = Flask(__name__)

        @self.app.route('/kut')
        def test():
            return Response('Hello World', 200)

        self.app.run('localhost',5123, False)

class KillThread(Thread):

    def __init__(self):
        super(KillThread,self).__init__()
        self.running = True

    def run(self):
        while self.running:
            print 'ZUIGERRRR ' + str(time.time())
            time.sleep(0.1)

    def kill(self):
        self.running = False

class KillerThread(Thread):
    def __init__(self,ttl, func):
        super(KillerThread,self).__init__()

        self.func = func
        self.ttl =ttl
        self.time = 0

    def run(self):
        while True:
            if self.time == self.ttl:
                self.func()
                return

            self.time += 1
            time.sleep(0.1)



def print_zuiger():
    while True:
        print 'ZUIGERRRR ' + str(time.time())
        time.sleep(0.1)

def main():
    # web = WebThread()
    # web.daemon = True

    # portal = Thread(target=print_zuiger)
    kill = KillThread()
    killer = KillerThread(100,kill.kill)
    try:
        # web.start()
        kill.start()
        killer.start()


        killer.join()
        kill.join()

        # i = 0
        # while True:
        #     if i > 10 :
        #         kill.kill()
        #     print kill.isAlive()
        #     time.sleep(1)
        #     i += 1
    except KeyboardInterrupt:
        exit(1)


if __name__ == '__main__':
    main()