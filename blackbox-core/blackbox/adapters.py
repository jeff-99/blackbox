import time, random
from gpxpy.parser import GPXParser
import gpsd
import os, sys, inspect
from time import mktime
from Adafruit_BNO055 import BNO055


class GPSPosition(object):
    def __init__(self):
        self.latitude   = None
        self.longitude  = None
        self.timestamp  = None
        self.altitude   = None # m
        self.eps        = None # geen idee
        self.epx        = None # geen idee
        self.epv        = None # geen idee
        self.ept        = None # geen idee
        self.velocity   = 0.0 # m/s
        self.climb      = None
        self.track      = None
        self.mode       = None
        self.satellites = None

    def get_kmh(self):
        return float(self.velocity) * 3.6

    def __repr__(self):
        return "{}, {}, {}".format(self.latitude,self.longitude,self.velocity)


class GPSAdapter(object):
    def __init__(self):
        gpsd.connect()
        self.previous_position = None

    def get_current_gps(self):

        gps_position = GPSPosition()

        try:
            packet = gpsd.get_current()

            lat, lon = packet.position()
            if (lat is None or lon is None) and self.previous_position is not None:
                return self.previous_position

            gps_position.latitude = lat
            gps_position.longitude = lon

            # error is really big without antenna, so we access speed directly
            gps_position.velocity = packet.hspeed

            gps_position.altitude = packet.altitude()
            gps_position.timestamp = packet.time
        except (Exception, gpsd.NoFixError):
            if not self.previous_position is None:
                return self.previous_position
            return gps_position

        self.previous_position = gps_position
        return gps_position



class MockGPSAdapter(object):

    def __init__(self):
        self.start_time = time.time()

        with open(os.path.join(os.path.dirname(__file__), 'dummydata/zuidhollandrit.gpx'),'r') as f:
            parser = GPXParser(f)
            gpx = parser.parse()

        route = gpx.routes[0]

        self.points = []
        self.total = 0
        self.velocity = 0
        for routepoint in route.points:
            velocity_mod = random.randint(-5, 5)
            self.velocity = abs(self.velocity + velocity_mod)
            self.points.append((routepoint.latitude,routepoint.longitude,self.velocity))
            self.total +=1

    def get_current_gps(self):
        t = time.time()

        sec_running = self.start_time - t

        i = int(sec_running) % self.total

        full_loops = int(sec_running / self.total)

        point = self.points[i]

        gps = GPSPosition()

        gps.latitude = point[0] + (full_loops * 0.5)
        gps.longitude = point[1] + (full_loops * 0.5)
        gps.velocity = point[2]

        return gps


class OrientationAdapter(object):
    def __init__(self):
        """
        Zwarte blokje op de sensor moet in de richting van de achterkant van de motor staan
        acceleratie naar voren is dan een positief getal op de x-as (linear_acceleration)

        en de pitch komt overeen met beweging in de z-as, zoals ook gedefinieerd in de video bewerking,
        dus -90 is links + 90 is rechts


        :return:
        """
        self.sensor = BNO055.BNO055(serial_port='/dev/ttyAMA0', rst=18)
        if not self.sensor.begin():
            raise Exception("Sensor can not be started!")

    def get_pitch(self):
        heading, roll, pitch = self.sensor.read_euler()
        return pitch

    def get_acceleration(self):
        x, y, z = self.sensor.read_linear_acceleration()
        return x

    def get_temperature(self):
        return self.sensor.read_temp()


class MockOrientationAdapter(object):
    def __init__(self):
        self.angle = 0

    def get_pitch(self):
        angle_mod = float(random.randint(-10,10))
        new_angle = self.angle + angle_mod
        if -90 < new_angle < 90:
            self.angle = new_angle

        return self.angle

    def get_acceleration(self):
        return random.randint(0,5)

    def get_temperature(self):
        return random.randint(20,25)


def get_adapter_class(name):
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if not name in [c[0] for c in clsmembers]:
        raise Exception("Adapter with name {} is not available".format(name))

    return getattr(sys.modules[__name__],name)