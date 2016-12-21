import json
import time


class MeasurementSet(object):

    def __init__(self, measurements = None):
        self.measurements = measurements or []

    def append(self, measurement):
        self.measurements.append(measurement)

    def _get_attr(self,attr):
        return list(map(lambda m: getattr(m,attr),self.measurements))

    def get_speeds(self):
        return self._get_attr('speed')

    def get_angles(self):
        return self._get_attr('angle')

    def get_gps(self):
        return list(zip(self._get_attr('latitude'),self._get_attr('longitude')))

    def get_timestamps(self):
        return self._get_attr('timestamp')

    def get_temperatures(self):
        return self._get_attr('temperature')

    def get_measurements(self):
        return self.measurements

    def get_last(self):
        return self.measurements[-1]


class Measurement(object):
    def __init__(self):
        self.timestamp    = time.time()
        self.latitude     = None
        self.longitude    = None
        self.speed        = None
        self.angle        = None
        self.acceleration = None
        self.temperature  = None

    def set_gps(self, gps_position):
        self.latitude = gps_position.latitude
        self.longitude = gps_position.longitude
        self.speed = gps_position.get_kmh()

    def set_angle(self, angle):
        self.angle = angle

    def set_acceleration(self, a):
        self.acceleration = a

    def set_temperature(self, temperature):
        self.temperature = temperature

    def to_json(self):
        return json.dumps({
            'timestamp' : self.timestamp,
            'latitude' : self.latitude,
            'longitude' : self.longitude,
            'speed' : self.speed,
            'angle' : self.angle,
            'temperature' : self.temperature,
            'acceleration' : self.acceleration
        })

    @classmethod
    def from_json(cls, data):
        data = json.loads(data)
        m = cls()
        for k,v in data.items():
            setattr(m,k,v)

        return m

    def to_tuple(self):
        return (self.timestamp,self.latitude,self.longitude,self.speed,self.angle,self.temperature,self.acceleration)

    def __repr__(self):
        return "{},{},{},{},{},{},{}".format(self.timestamp,self.latitude,self.longitude,self.speed,self.angle,self.temperature,self.acceleration)


class MeasurementDiff(Measurement):

    def __init__(self,m1,m2):
        self.old = m1
        self.timestamp   = m2.timestamp - m1.timestamp
        self.latitude    = m2.latitude - m1.latitude
        self.longitude   = m2.longitude - m1.longitude
        self.speed       = m2.speed - m1.speed
        self.angle       = m2.angle - m1.angle
        self.temperature = m2.temperature - m1.temperature
        self.acceleration = m2.acceleration - m1.acceleration
