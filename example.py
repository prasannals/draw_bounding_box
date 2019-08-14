from draw_bounding_box import DrawBoundingBox
import cv2
from functools import partial

def get_box_info():
    return [('prasanna', [10, 10, 150, 150])
        , ('reyaan', [250, 250, 400, 400])]

def image_from_cv(read):
    # return None if ret == False else return frame
    ret, frame = read()
    return frame if ret else None

URL = 'rtsp://admin:123456@192.168.1.13/live/ch0'
vcap = cv2.VideoCapture(URL)
bbox = DrawBoundingBox(get_box_info, partial(image_from_cv, read=vcap.read))
bbox.run()