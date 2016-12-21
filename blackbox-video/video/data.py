import csv
from blackbox.measurement import Measurement, MeasurementSet, MeasurementDiff


def get_measurements_from_file(file):
    """
    Read csv and return measurements object

    :param file:
    :return:
    """
    measurements = []

    with open(file, 'r') as f:
        reader = csv.reader(f)
        for timestamp,latitude,longitude,speed,angle,temperature,acceleration in reader:

            m = Measurement()
            m.timestamp = float(timestamp)
            m.latitude = float(latitude)
            m.longitude = float(longitude)
            m.speed = float(speed)
            m.angle = float(angle)
            m.temperature = float(temperature)
            m.acceleration = float(acceleration)

            measurements.append(m)

    return measurements


class MeasurementDivider(object):
    def __init__(self, measurements, frame_count, fps):
        self.measurements = measurements
        self.compiled_measurements = MeasurementSet()
        self.frame_count = frame_count
        self.fps = fps

    @staticmethod
    def _divide(previous_measurement, current_measurement, count):
        """
        Calculate the diffs between to measurements
        and return new measurements based on the count

        :param previous_measurement:
        :param m:
        :param count:
        :return:
        """
        diff = MeasurementDiff(previous_measurement,current_measurement)

        new_measurements = []

        for i in range(count):
            m = Measurement()
            m.timestamp = diff.old.timestamp + ((diff.timestamp / count) * i)
            m.latitude = diff.old.latitude + ((diff.latitude / count) * i)
            m.longitude = diff.old.longitude + ((diff.longitude / count) * i)
            m.speed = diff.old.speed + ((diff.speed / count) * i)
            m.angle = diff.old.angle + ((diff.angle / count) * i)

            new_measurements.append(m)

        return new_measurements

    def _compile(self):
        """
        There should be about 10 measurements per second
        vs
        30-60 frames per second.

        To allow a smooth transition between frames were gonna divide the measurements between those frames
        By calculating the diffs between the measurements and evenly distributing the changes to the frames

        :return: MeasurementSet
        """
        # given that the FPS is fairly stable we can calculate the time each frame lasts
        total_time = self.measurements[-1].timestamp - self.measurements[0].timestamp
        time_per_frame = float(total_time) / float(self.frame_count)

        # give every frame a timestamp based on the total measured time
        frames = [self.measurements[0].timestamp + (time_per_frame * i) for i in range(self.frame_count)]

        # pop the first measurement as a baseline
        previous_measurement = self.measurements.pop(0)
        for m in self.measurements:

            # fetch the number of frames since last measurement
            frames_for_measurement = 0
            while len(frames) > 0 and frames[0] <= m.timestamp:
                frames.pop(0)  # delete the frames when used ( pop is an O(n) operation, needs optimization)
                frames_for_measurement += 1

            # based on the number of frames since last measurement, create new measurements
            new_measurements = self._divide(previous_measurement,m,frames_for_measurement)
            for new in new_measurements:
                self.compiled_measurements.append(new)

            previous_measurement = m

        return self.compiled_measurements

    def extract(self):
        return self._compile()