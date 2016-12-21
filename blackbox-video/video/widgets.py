import cv2
import numpy as np
import math


class Widget(object):
    def __init__(self):
        self.width = 100
        self.height = 100
        self.pos = (0,0)

    def draw(self,i, frame):
        raise NotImplementedError()

    def set_pos(self,position):
        self.pos = position

    def set_width(self,width):
        self.width = width

    def set_height(self,height):
        self.height = height

    def set_fps(self,fps):
        self.fps = fps

    def set_total_frame_count(self, total_frame_count):
        self.total_frame_count = total_frame_count

    def set_render_range(self, start_frame, end_frame):
        self.start_frame = start_frame
        self.end_frame   = end_frame


class MapWidget(Widget):
    def __init__(self, points):
        super(MapWidget, self).__init__()

        self.points = points
        self.remapped_points = []

        x_min = float(min([l[0] for l in points]))
        x_max = float(max([l[0] for l in points]))

        y_min = float(min(l[1] for l in points))
        y_max = float(max(l[1] for l in points))

        # resize the min/max values to create equal domains
        x_domain = (x_max - x_min)
        y_domain = (y_max - y_min)

        if x_domain > y_domain:
            y_adjustment = x_domain / 2.0
            y_min -= y_adjustment
            y_max += y_adjustment
        elif x_domain < y_domain:
            x_adjustment = y_domain / 2.0
            x_min -= x_adjustment
            x_max += x_adjustment
        else:
            #same size so no adjustment needed
            pass

        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def set_pos(self,position):
        self.pos = position

    def set_height(self, height):
        self.height = height

    def set_width(self, width):
        self.width = width

    def get_point(self, i):
        p = self.points[i]

        remapped_x = remap(p[0],self.x_min,self.x_max,0,self.width)
        remapped_y = remap(p[1],self.y_min,self.y_max,0,self.height)
        new_pos = (self.pos[0] + remapped_x, self.pos[1] + remapped_y)

        return new_pos

    def draw_position(self,t, frame):
        curpos = self.get_point(t)
        cv2.circle(frame,curpos,10,0,10)

    def draw_whole_map(self,frame):
        cv2.polylines(frame, np.int32([self.remapped_points]),False,255,5)

    def draw_map(self, t, frame):
        for i in range(t+1):
            if i - 1 > 0:
                pos1 = self.get_point(i - 1)
                pos2 = self.get_point(i)

                cv2.line(frame, pos1,pos2,255,5)

    def draw(self,i, frame):
        self.draw_map(i, frame)
        self.draw_position(i,frame)


class OptimizedMapWidget(MapWidget):
    def __init__(self, fps, points):
        super(OptimizedMapWidget, self).__init__(points)
        self.rendered_points = []
        self.fps = fps

    def _draw_before_start(self):
        if len(self.rendered_points) == 0:
            for t in range(0, self.start_frame):
                self._add_point(t)

    def _add_point(self,t):
        pos2 = self.get_point(t)
        self.rendered_points.append(pos2)

    def draw_map(self, t, frame):
         self._draw_before_start()
         if t - 1 > 0 and t % (int(self.fps) / 2) == 0:
                self._add_point(t)

         cv2.polylines(frame, np.int32([self.rendered_points]),False,255,5)


def remap( x, oldMinimum, oldMaximum, newMinimum, newMaximum ):

    #range check
    if oldMinimum == oldMaximum:
        print("Warning: Zero input range")
        return None

    if newMinimum == newMaximum:
        print("Warning: Zero output range")
        return None

    #check reversed input range
    reverseInput = False
    oldMin = min( oldMinimum, oldMaximum )
    oldMax = max( oldMinimum, oldMaximum )
    if not oldMin == oldMinimum:
        reverseInput = True

    #check reversed output range
    reverseOutput = False
    newMin = min( newMinimum, newMaximum )
    newMax = max( newMinimum, newMaximum )
    if not newMin == newMinimum :
        reverseOutput = True

    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
    if reverseInput:
        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return int(result)


class LeanAngleWidget(Widget):
    def __init__(self, angles, speeds):
        self.angles = angles
        self.speeds = speeds

        self.height = 100

    def set_height(self, height):
        self.radius = height

    def set_pos(self, position):
        self.center = (position[0] + self.radius , position[1] + self.radius)

    def maxLeanLeft(self,t):
        if t == 0:
            return 0
        return min(0, min(self.angles[0:t]))

    def maxLeanRight(self, t):
        if t == 0:
            return 0
        return max(0, max(self.angles[0:t]))

    def get_speed(self,t):
        return self.speeds[t]

    @staticmethod
    def _complete_radii(radii):
        return radii + [x for x in reversed(radii)]

    @staticmethod
    def _complete_anglemods(anglemods):
        return anglemods + [x * -1 for x in reversed(anglemods)]

    def draw_angle(self, t, frame):
        # angle = self.angles[t]

        center = (100,100)

        radii = [
            100,
            10,
            10
        ]
        mapped_polygon = []

        for i,r in enumerate(radii):
            angle = self.angles[t] - 90
            radius = r

            if i == 1:
                angle = angle - 90

            if i == 2:
                angle = angle + 90

            angle = math.radians(angle)

            x = center[0] + (radius * math.cos(angle))
            y = center[1] + (radius * math.sin(angle))

            mapped_polygon.append((x,y))

        # print polygon
        # print mapped_polygon
        # exit()
        cv2.fillPoly(frame,np.int32([mapped_polygon]),255)
        cv2.circle(frame,center,10,100)
        cv2.circle(frame,center,100,100)

    def draw_min_max(self, t, overlay):

        minAngle = self.maxLeanLeft(t)
        if minAngle < 0:
            x = self.center[0] + (self.radius * math.cos(math.radians(minAngle - 90)))
            y = self.center[1] + (self.radius * math.sin(math.radians(minAngle - 90)))
            cv2.line(overlay,self.center, (int(x),int(y)),  (0,0,255),3)

        maxAngle = self.maxLeanRight(t)
        if maxAngle > 0:
            x2 = self.center[0] + (self.radius * math.cos(math.radians(maxAngle - 90)))
            y2 = self.center[1] + (self.radius * math.sin(math.radians(maxAngle - 90)))
            cv2.line(overlay,self.center,(int(x2),int(y2)), (0,0,255), 3)

    def draw_gauge(self, frame):
        radius = self.radius
        center = self.center
        outer_axes = (radius, radius)
        inner_axes= (int(radius * 0.90), int(radius *0.90))
        angle = 0
        startAngle = 180
        endAngle = 360
        thickness = -1

        cv2.ellipse(frame, center, outer_axes, angle, startAngle, endAngle, (0,0,0), thickness)
        cv2.ellipse(frame, center, inner_axes, angle, startAngle, endAngle, (255,255,255), thickness)

        for angle in range(-180,20,20):
            outer_x = self.center[0] + ((self.radius - 5) * math.cos(math.radians(angle)))
            outer_y = self.center[1] + ((self.radius - 5) * math.sin(math.radians(angle)))

            inner_x = self.center[0] + ((self.radius - 40) * math.cos(math.radians(angle)))
            inner_y = self.center[1] + ((self.radius - 40) * math.sin(math.radians(angle)))

            cv2.line(frame, (int(outer_x),int(outer_y)), (int(inner_x),int(inner_y)),(0,0,0),10)

    def draw_dash(self,t,frame):
        dash_height = 75
        dash_width = self.radius + 25

        top_left = (self.center[0] - dash_width , self.center[1])
        bottom_right = (self.center[0] + dash_width, self.center[1] + dash_height)

        cv2.rectangle(frame, top_left,bottom_right,(0,0,0),-1)

        dash_panel_height = 45
        dash_panel_width = self.radius
        dash_panel_top_left = (top_left[0] + (int(self.radius * 0.5) + 25) , int(top_left[1] + ((dash_height - dash_panel_height) / 2)))
        dash_panel_bottom_right = (dash_panel_top_left[0] + dash_panel_width , int(dash_panel_top_left[1] + dash_panel_height))

        cv2.rectangle(frame, dash_panel_top_left,dash_panel_bottom_right,(255,255,255),-1)

        speed_origin = (dash_panel_top_left[0] + 35,dash_panel_top_left[1] + (int(dash_panel_height * 0.75)))

        text = str(int(self.get_speed(t)))
        cv2.putText(frame,text,speed_origin,cv2.FONT_HERSHEY_DUPLEX,1,(0,0,0))

        text_origin = (speed_origin[0] + 70, speed_origin[1])

        cv2.putText(frame,'km/h',text_origin,cv2.FONT_HERSHEY_DUPLEX,1,(0,0,0))

    def draw(self,i, frame):
        self.draw_gauge(frame)
        self.draw_dash(i, frame)
        self.draw_min_max(i,frame)
        self.draw_angle(i, frame)




class LeanAngleWidget2(LeanAngleWidget):

    def draw_angle(self, t, frame):

        radii_helmet = [
            1     * self.radius,
            1     * self.radius,
            0.85  * self.radius,
            0.85  * self.radius,
        ]
        angle_mods_helmet = [
            0,
            7,
            8,
            0
        ]

        radii_bike = [
            0.85  * self.radius,
            0.87  * self.radius,
            0.40  * self.radius,
            0.32  * self.radius
        ]

        angle_mods_bike = [
             0,
            20,
            40,
            0
         ]

        radii_wheel = [
            0.32  * self.radius,
            0.32  * self.radius,
            0.10  * self.radius,
            0     * self.radius
         ]

        angle_mods_wheel = [
             0,
            18,
            90,
            0,
         ]

        shapes =[
             (radii_helmet,angle_mods_helmet,(0,0,255)),
             (radii_bike,angle_mods_bike,(255,0,0)),
             (radii_wheel,angle_mods_wheel, (0,0,0)),
         ]

        for radii_right, angle_mods_right, color in shapes:
            radii = self._complete_radii(radii_right)
            angle_mods = self._complete_anglemods(angle_mods_right)

            mapped_polygon = []

            for i,r in enumerate(radii):
                angle = self.angles[t] - 90
                radius = r

                angle = angle + angle_mods[i]

                angle = math.radians(angle)

                x = self.center[0] + (radius * math.cos(angle))
                y = self.center[1] + (radius * math.sin(angle))

                mapped_polygon.append((x,y))

            cv2.fillPoly(frame,np.int32([mapped_polygon]),color)


class TimerWidget(Widget):
    def __init__(self):
        super(TimerWidget,self).__init__()

    def draw(self,i, frame):
        seconds = math.floor(float(i) / float(self.fps))

        cv2.putText(frame,str(seconds),self.pos,cv2.FONT_HERSHEY_DUPLEX,1,(0,0,0))
