from datafetcher import DataFetcher

import sys
sys.path.append("/home/jeff/dev/blackbox-tryout")
from blackbox.measurement import Measurement, MeasurementSet

class Frame(object):
    def __init__(self,index,timestamp,data=None):
        self.index = index
        self.timestamp = timestamp
        self.data = data

    def __repr__(self):
        data = ''
        if 'measurement' in self.data and self.data['measurement'] is not None:
            strings = list(map(str,self.data['measurement'].to_tuple()))
            data =','.join(strings)
        return 'Frame {} - {} - {}'.format(self.index,self.timestamp, data)

class DataSyncer(object):
    """
    @TODO Dit moet echt beter worden getest!!!!!!
    """
    def __init__(self, measurmentdata, frame_count, fps):
        self.data = measurmentdata
        self.frame_count = frame_count
        self.fps = fps

    def combine(self,measurements):
        """
        Get averages for given measurements
        :param measurements:
        :return:
        """
        count = float(len(measurements))
        avg_angle = float(sum([m.angle for m in measurements])) / count
        avg_speed = float(sum([m.speed for m in measurements])) / count
        avg_latitude = float(sum([m.latitude for m in measurements])) / count
        avg_longitude = float(sum([m.longitude for m in measurements])) / count

        m = Measurement()
        m.latitude = avg_latitude
        m.longitude = avg_longitude
        m.speed = avg_speed
        m.angle = avg_angle

        return m


    def _compile(self):
        timestamps = [m.timestamp for m in self.data]
        start = min(timestamps)
        stop = max(timestamps)
        delta_per_frame = (stop - start) / self.frame_count

        mSet = MeasurementSet()
        previous_frame_timestamp = None
        previous_measuremnt = None
        for index in range(0,self.frame_count):
            frame_timestamp = start + (index * delta_per_frame)
            if not previous_frame_timestamp is None:
                diff = frame_timestamp - previous_frame_timestamp
                if index > 290:
                    alala=1
                """
                Try to fetch all measurements between this frame and the previous frame
                if there are no measurments available we copy the previous measurement
                """
                measurements = filter(lambda m: previous_frame_timestamp <= m.timestamp <= frame_timestamp ,self.data)
                if len(measurements) == 0:
                    measurements = [previous_measuremnt]

                measurement = self.combine(measurements)
                previous_measuremnt = measurement
                mSet.append(measurement)

            previous_frame_timestamp = frame_timestamp

        #dirty hack to get a equal amount of frames/measurements
        mSet.append(measurement)

        return mSet

    def extract(self):
        return self._compile()

if __name__ == '__main__':
    dt = DataFetcher('data.csv')
    time = 240

    d = DataSyncer(dt.get_all(),10,1)
    print(d.extract())