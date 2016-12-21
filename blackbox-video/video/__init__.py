import cv2
import sys
from .data import get_measurements_from_file, MeasurementDivider
from .widgets import OptimizedMapWidget, MapWidget, LeanAngleWidget2, TimerWidget, Widget


class Video(object):
    def __init__(self, filepath):
        self.filepath = filepath

        self.cap = cv2.VideoCapture(filepath)

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width  = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.codec = int(self.cap.get(cv2.CAP_PROP_FOURCC))

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

    data = get_measurements_from_file(data_file)

    divider = MeasurementDivider(data, video.frames, video.fps)
    mSet= divider.extract()

    angles = mSet.get_angles()
    speeds = mSet.get_speeds()
    points = mSet.get_gps()

    video_processor = VideoProcessor(video, start_frame,end_frame)

    map_height = 350
    map_y = int(video.height * 0.9) - map_height

    map_width = 350
    map_x = int(video.width*0.9) - map_width

    drawer = OptimizedMapWidget(video.fps,points)
    drawer.set_width(map_width)
    drawer.set_height(map_width)

    video_processor.add_widget(drawer,(map_x,map_y))

    leaner = LeanAngleWidget2(angles, speeds)
    leaner.set_height(200)

    leaner_x = int(video.width * 0.1)         # 10% from left
    leaner_y = int(video.height * 0.9) - 250  # 90% from top - 250 pixels

    video_processor.add_widget(leaner, (leaner_x, leaner_y))

    # timer = TimerWidget()
    # video.add_widget(timer,(100,100))

    writer = cv2.VideoWriter(output_file,cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),video.fps,(video.width,video.height))
    for frame in video_processor.get_frames():
        writer.write(frame)

    cv2.destroyAllWindows()
    writer.release()
