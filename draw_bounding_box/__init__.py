import cv2
import pdb
from time import time
import os
from voc_xml import VOCAnnotation, object_xml

def get_fname():
    return str(time()).replace('.', '_')

def draw_label_and_box(img, label, box, font_args):
    cv2.rectangle(img, tuple( (int(box[0]), int(box[1])) ), tuple( (int(box[2]), int(box[3])) ), 
        font_args['box_color'], font_args['box_thickness'] )

    cv2.putText(img, label, tuple( (int(box[0]), int(box[1])) ), 
        font_args['font'], font_args['font_scale'], 
        font_args['font_color'], font_args['line_type'])

def cv_loop(run_func, quit_key='q'):
     while True:
        if (cv2.waitKey(2) & 0xFF) == ord(quit_key):
            cv2.destroyAllWindows()
            break
        else:
            run_func()

get_cur_dir = lambda path: os.path.abspath(path).split('/')[-1]

def write_voc_pascal(img, box_params, path='.', img_fmt = '.jpg'):
    fname = get_fname() 
    img_name = fname + img_fmt
    cv2.imwrite(os.path.join(path, img_name) , img)
    voc = VOCAnnotation(get_cur_dir(path), img_name, os.path.abspath(path), 
            img.shape[1], img.shape[0], img.shape[2])
    for param in box_params:
        voc.add_object(object_xml(param[0], int(param[1][0]), int(param[1][1]), int(param[1][2]), int(param[1][3])) )
    voc.write_to_file(os.path.join(path, fname + '.xml'))

class DrawBoundingBox():
    def __init__(self, get_box_params, get_image, window_title='Bounding Box', quit_key='q',
        font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.5, font_color=(0,0,0), line_type=2,
        box_thickness=2, box_color=(0,255,0), img_dir='.'):
        '''
        get_box_params - function - takes in an image (numpy array) should 
        return a list of tuples where the first element of the tuple is the 
        label of the box and the second 
        element is a list of 4 numbers representing the coordinates of the
        bounding box [x_top_left, y_top_left, x_bottom_right, y_bottom_right]

        get_image - function - should return the next frame (numpy array)
        each time it is called
        '''
        self.get_box_params, self.get_image = get_box_params, get_image
        self.WINDOW_TITLE, self.quit_key, self.img_dir = window_title, quit_key, img_dir
        self.font_args = {'font':font, 'font_scale':font_scale, 
                'font_color':font_color, 'line_type':line_type,
                'box_thickness':box_thickness, 'box_color':box_color}

    def run(self):
        cv_loop(self._draw_box, quit_key=self.quit_key)
    
    def _draw_box(self):
        img = self.get_image()
        box_params = self.get_box_params(img)
        write_voc_pascal(img, box_params, path=self.img_dir)
        list(map(lambda arg: draw_label_and_box(img, arg[0], 
                    arg[1], self.font_args), box_params))
        cv2.imshow(self.WINDOW_TITLE, img)