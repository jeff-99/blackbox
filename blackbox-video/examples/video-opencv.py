import cv2
import numpy as np
# from __future__ import print_function
from gpxtest import get_points
import math
import sys
from postprocess import PostProcessor
from datafetcher import DataFetcher
from sync import DataSyncer
from divider import MeasurementDivider
import multiprocessing
from multiprocessing.queues import Empty
import time
from widgets import *


class Video(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.widgets = []

        self.cap = cv2.VideoCapture(filepath)

        self.fps = int(self.cap.get(cv2.cv.CV_CAP_PROP_FPS))
        self.frames = int(self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        self.width  = int(self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

    def add_widget(self,widget,position):
        if isinstance(widget,Widget):
            widget.set_fps(self.fps)
            widget.set_total_frame_count(self.frames)
            widget.set_pos(position)
            self.widgets.append(widget)

    def get_frames(self,start = None,end = None):
        start = start or 0
        end = end or self.frames

        self.cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,start)
        for i in range(start,end):
            flag, frame = self.cap.read()

            overlay = frame.copy()

            for widget in self.widgets:
                widget.draw(i, frame)

            sys.stdout.write('\r')
            sys.stdout.write("rendering frame: " + str(i+1) + " / " + str(self.frames))
            sys.stdout.flush()

            cv2.addWeighted(overlay,0.5,frame,1-0.5,0,frame)

            yield frame

def process_frames(filename,output_file, start_frame=None,end_frame=None):
    video = Video(filename)

    # print video.frames;exit()

    map_height = 500
    map_y = int(video.height * 0.9) - map_height

    map_width = 500
    map_x = int(video.width*0.9) - map_width

    data = DataFetcher('./input/201611131239_results.csv')

    divider = MeasurementDivider(data.get_measurements(), video.frames, video.fps)
    mSet= divider.extract()
    angles = mSet.get_angles()
    speeds = mSet.get_speeds()
    points = mSet.get_gps()

    drawer = MapWidget(points)
    drawer.set_width(map_width)
    drawer.set_height(map_width)
    video.add_widget(drawer,(map_x,map_y))

    # leaner = LeanAngleDrawer(range(-90,90))

    leaner = LeanAngleWidget2(angles, speeds)
    leaner.set_height(250)
    video.add_widget(leaner, (int(video.width * 0.1),int(video.height * 0.9) - 250))

    timer = TimerWidget()
    video.add_widget(timer,(100,100))

    # output_file = 'output/test3.avi'
    writer = cv2.VideoWriter(output_file,cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'),video.fps,(video.width,video.height))
    for frame in video.get_frames(start_frame,end_frame):
        writer.write(frame)

    cv2.destroyAllWindows()
    writer.release()

########################################
#
# Single processing setup!
#
########################################

single_start = time.time()

# filename = './input/00027.m4v'
filename = './input/kneedown.MP4'
output_file = 'output/test3.avi'

process_frames(filename,output_file,0,10)

print "\npostprocessing!!"
p = PostProcessor(filename, output_file)
p.process()
print "completed!"

single_finish = time.time()
###########################################
#
# Multiprocessing setup
#
###########################################

mp_start = time.time()
#

video = Video(filename)
frames_per_process = math.ceil(float(video.frames) / float(multiprocessing.cpu_count()))
total_frames = 10 or video.frames

frame_batches = [(int(x),int(x+frames_per_process-1) if x+frames_per_process-1 <= total_frames else total_frames) for x in range(0,total_frames,int(frames_per_process))]
processes =[]
output_files =[]
for i,batch in enumerate(frame_batches):
    filename = './input/kneedown.MP4'
    output_filename = 'output/test3-multi-{}.avi'.format(i)
    output_files.append(output_filename)

    p = multiprocessing.Process(target=process_frames, args=(filename,output_filename,batch[0],batch[1]))
    processes.append(p)
    p.start()

for i,p in enumerate(processes):
    p.join()

print filename, output_files
post = PostProcessor(filename,output_files)
post.process()

cv2.destroyAllWindows()
#
mp_finish = time.time()
#
print("Single process time : {} \n Multi process time : {}\n Difference in % : {}".format((single_finish-single_start),(mp_finish -mp_start),(((mp_finish -mp_start) - (single_finish-single_start))/(single_finish-single_start))))