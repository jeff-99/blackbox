import csv
import sys
sys.path.append("/home/jeff/dev/blackbox-tryout")
from blackbox.measurement import Measurement

class DataFetcher(object):
    def __init__(self,file):
        self.file = file
        self.angles = []
        self.speeds = []
        self.gps    = []
        self.timestamps = []
        self.measurments = []
        self.temperatures = []
        self.accelerations = []
        self.processed = False

    def read(self):
        with open(self.file, 'r') as f:
            reader = csv.reader(f)
            for timestamp,latitude,longitude,speed,angle,temperature,acceleration in reader:
                self.timestamps.append(float(timestamp))
                self.angles.append(float(angle))
                self.speeds.append(float(speed))
                self.gps.append((float(latitude),float(longitude)))
                self.temperatures.append(float(temperature))
                self.accelerations.append(float(acceleration))

                m = Measurement()
                m.timestamp = float(timestamp)
                m.latitude = float(latitude)
                m.longitude = float(longitude)
                m.speed = float(speed)
                m.angle = float(angle)
                m.temperature = float(temperature)
                m.acceleration = float(acceleration)

                self.measurments.append(m)

    def get_speeds(self):
        if not self.processed:
            self.read()
        return self.speeds

    def get_angles(self):
        if not self.processed:
            self.read()
        return self.angles

    def get_gps(self):
        if not self.processed:
            self.read()
        return self.gps

    def get_timestamps(self):
        if not self.processed:
            self.read()
        return self.timestamps

    def get_measurements(self):
        if not self.processed:
            self.read()
        return self.measurments

    def get_all(self):
        if not self.processed:
            self.read()
        return zip(self.timestamps,self.gps,self.angles,self.speeds)