import cv2
import sys
from .datafetcher import DataFetcher
from .divider import MeasurementDivider
from .widgets import OptimizedMapWidget, MapWidget, LeanAngleWidget2, TimerWidget, Widget


class Video(object):
    def __init__(self, filepath):
        self.filepath = filepath
        # self.widgets = []

        self.cap = cv2.VideoCapture(filepath)

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width  = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.codec = int(self.cap.get(cv2.CAP_PROP_FOURCC))

    # def add_widget(self,widget,position):
    #     if isinstance(widget,Widget):
    #         widget.set_fps(self.fps)
    #         widget.set_total_frame_count(self.frames)
    #         widget.set_pos(position)
    #         self.widgets.append(widget)

    # def get_frames(self,start = None,end = None):
    #     start = start or 0
    #     end = end or self.frames
    #
    #     self.cap.set(cv2.CAP_PROP_POS_FRAMES,start)
    #     for i in range(start,end):
    #         flag, frame = self.cap.read()
    #
    #         overlay = frame.copy()
    #
    #         for widget in self.widgets:
    #             widget.draw(i, frame)
    #
    #         sys.stdout.write('\r')
    #         sys.stdout.write("rendering frame: " + str(i+1) + " / " + str(self.frames))
    #         sys.stdout.flush()
    #
    #         # cv2.addWeighted(overlay,0.5,frame,1-0.5,0,frame)
    #
    #         yield frame

    def set_current_frame(self,frame_number):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES,frame_number)

    def read(self):
        return self.cap.read()



class VideoProcessor(object):
    def __init__(self, video, start_frame=None, end_frame=None):
        self.video = video
        self.start_frame = start_frame or 0
        self.end_frame = end_frame or video.frames
        self.widgets = []

    def add_widget(self,widget,position):
        if isinstance(widget,Widget):
            widget.set_fps(self.video.fps)
            widget.set_total_frame_count(self.video.frames)
            widget.set_render_range(self.start_frame,self.end_frame)
            widget.set_pos(position)
            self.widgets.append(widget)

    def get_frames(self):

        self.video.set_current_frame(self.start_frame)
        for i in range(self.start_frame,self.end_frame):
            flag, frame = self.video.read()

            overlay = frame.copy()

            for widget in self.widgets:
                widget.draw(i, frame)

            sys.stdout.write('\r')
            sys.stdout.write("rendering frame: " + str(i+1) + " / " + str(self.video.frames))
            sys.stdout.flush()

            # cv2.addWeighted(overlay,0.5,frame,1-0.5,0,frame)

            yield frame


def process_frames(filename, output_file, data_file, start_frame=None,end_frame=None):
    """

    :param filename:
    :param output_file:
    :param data_file:
    :param start_frame:
    :param end_frame:
    :return:
    """
    video = Video(filename)

    # print video.frames;exit()

    map_height = 350
    map_y = int(video.height * 0.9) - map_height

    map_width = 350
    map_x = int(video.width*0.9) - map_width

    data = DataFetcher(data_file)
    # angles = data.get_angles()
    # speeds = data.get_speeds()
    # points = data.get_gps()

    divider = MeasurementDivider(data.get_measurements(), video.frames, video.fps)
    mSet= divider.extract()
    angles = mSet.get_angles()

    speeds = mSet.get_speeds()
    points = mSet.get_gps()

    video_processor = VideoProcessor(video, start_frame,end_frame)

    drawer = OptimizedMapWidget(video.fps,points)
    # drawer = MapWidget(points)
    drawer.set_width(map_width)
    drawer.set_height(map_width)
    video_processor.add_widget(drawer,(map_x,map_y))

    leaner = LeanAngleWidget2(angles, speeds)
    leaner.set_height(200)
    video_processor.add_widget(leaner, (int(video.width * 0.1),int(video.height * 0.9) - 250))

    # timer = TimerWidget()
    # video.add_widget(timer,(100,100))

    # output_file = 'output/test3.avi'
    # cv2.cv.CV_FOURCC('X', '2', '6', '4')
    # cv2.VideoWriter_fourcc('X', '2', '6', '4')

    writer = cv2.VideoWriter(output_file,cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),video.fps,(video.width,video.height))
    for frame in video_processor.get_frames():
        writer.write(frame)

    cv2.destroyAllWindows()
    writer.release()
