import math, sys
sys.path.append("/home/jeff/dev/blackbox-tryout")
from blackbox.measurement import Measurement, MeasurementSet, MeasurementDiff

class MeasurementDivider(object):
    def __init__(self, measurements, frame_count, fps):
        self.measurements = measurements
        self.compiled_measurements = MeasurementSet()
        self.frame_count = frame_count
        self.fps = fps

    def _divide(self,previous_measurement, m, count):
        diff = MeasurementDiff(previous_measurement,m)

        new_measurements =[]

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
        # given that the FPS is fairly stable we can calculate the time each frame lasts
        total_time = self.measurements[-1].timestamp - self.measurements[0].timestamp
        time_per_frame = float(total_time) / float(self.frame_count)

        # give every frame a timestamp based on the total measured time
        frames = [self.measurements[0].timestamp + (time_per_frame * i) for i in range(self.frame_count)]

        for i, m in enumerate(self.measurements):
            # skip the first measurement
            if i == 0:
                previous_measurement = self.measurements[0]
                continue

            # fetch the number of frames since last measurement
            frames_for_measurement = 0
            while len(frames) > 0 and frames[0] <= m.timestamp:
                frames.pop(0) # delete the frames when used ( pop is an O(n) operation, needs optimization)
                frames_for_measurement += 1

            # based on the number of frames since last measurement, create new measurements
            new_measurements = self._divide(previous_measurement,m,frames_for_measurement)
            for new in new_measurements:
                self.compiled_measurements.append(new)


            previous_measurement = m

        return self.compiled_measurements


    # def __compile(self):
    #     frames_per_m = int(math.ceil(float(self.frame_count) / float(len(self.measurements)-1)))
    #
    #     for i, m in enumerate(self.measurements):
    #         if i == 0:
    #             previous_measurement = self.measurements[0]
    #             continue
    #
    #         new_measurements = self._divide(previous_measurement,m,frames_per_m)
    #         for new in new_measurements:
    #             self.compiled_measurements.append(new)
    #
    #         previous_measurement = m
    #     return self.compiled_measurements

    def extract(self):
        return self._compile()