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

def cv_loop_on_key(run_func, quit_key='q', next_key='n'):
    run_func()
    while True:
        key_pressed = (cv2.waitKey(2) & 0xFF)
        if key_pressed == ord(quit_key):
            cv2.destroyAllWindows()
            break
        elif key_pressed == ord(next_key):
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
    def __init__(self, get_box_params, get_image, post_calc=None, window_title='Bounding Box', quit_key='q',
        font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.5, font_color=(0,0,0), line_type=2,
        box_thickness=2, box_color=(0,0,255), pred_box_color=(0,255, 0), img_dir='.'):
        '''
        post_calc - function - first argument will be an image (numpy array)
        second arguement will be a list of tuples representing the actual list 
        of labels and boxes for the image third argument will also be a list 
        of tuples representing the predicted list of labels and boxes for the image
        post_calc(img, y_box_params, box_params)

        get_box_params - function - takes in an image (numpy array) should 
        return a list of tuples where the first element of the tuple is the 
        label of the box and the second 
        element is a list of 4 numbers representing the coordinates of the
        bounding box [x_top_left, y_top_left, x_bottom_right, y_bottom_right]

        get_image - function - should return a tuple - first element should
        be the next image (numpy array). second element should be a list of 
        tuples where each entry is of form (label, bbox)
        '''
        self.get_box_params, self.get_image = get_box_params, get_image
        self.WINDOW_TITLE, self.quit_key, self.img_dir = window_title, quit_key, img_dir
        self.box_color, self.pred_box_color = box_color, pred_box_color
        self.post_calc = post_calc
        self.font_args = {'font':font, 'font_scale':font_scale, 
                'font_color':font_color, 'line_type':line_type,
                'box_thickness':box_thickness, 'box_color':box_color}

    def run(self):
        cv_loop(self._draw_box, quit_key=self.quit_key)
    
    def _draw_box(self):
        img, y_box_params = self.get_image()
        if img is not None: 
            box_params = self.get_box_params(img)
            print(box_params)
            write_voc_pascal(img, box_params, path=self.img_dir)
            self.font_args['box_color'] = self.box_color
            list(map(lambda arg: draw_label_and_box(img, arg[0], 
                        arg[1], self.font_args), box_params))
            self.font_args['box_color'] = self.pred_box_color
            list(map(lambda arg: draw_label_and_box(img, arg[0], 
                        arg[1], self.font_args), y_box_params))
            self.post_calc(img, y_box_params, box_params)
            cv2.imshow(self.WINDOW_TITLE, img)

def image_from_cv(read):
    # return None if ret == False else return frame
    ret, frame = read()
    return frame if ret else None

class DrawBoundingBoxOnNext(DrawBoundingBox):
    def __init__(self, get_box_params, get_image, post_calc=None, window_title='Bounding Box', quit_key='q',
        font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.5, font_color=(0,0,0), line_type=2,
        box_thickness=2, box_color=(0,0,255), pred_box_color=(0,255, 0), img_dir='.', next_key='n'):
        '''
        get_box_params - function - takes in an image (numpy array) should 
        return a list of tuples where the first element of the tuple is the 
        label of the box and the second 
        element is a list of 4 numbers representing the coordinates of the
        bounding box [x_top_left, y_top_left, x_bottom_right, y_bottom_right]

        get_image - function - should return a tuple - first element should
        be the next image (numpy array). second element should be a list of 
        tuples where each entry is of form (label, bbox)

        next_key - character - next image is obtained and its bounding box is displayed
                when the user clicks this key
        '''
        super().__init__(get_box_params, get_image, window_title=window_title, 
            quit_key=quit_key, font=font, font_scale=font_scale, font_color=font_color, 
            line_type=line_type, box_thickness=box_thickness, box_color=box_color, 
            pred_box_color=pred_box_color, img_dir=img_dir, post_calc=post_calc)
        self.next_key = next_key
        
    def run(self):
        cv_loop_on_key(self._draw_box, quit_key=self.quit_key, next_key=self.next_key)


class OpenCVBoundingBox(DrawBoundingBox):
    def __init__(self, get_box_params, cam_num=0, window_title='Bounding Box', post_calc=None, quit_key='q',
        font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.5, font_color=(0,0,0), line_type=2,
        box_thickness=2, box_color=(0,0,255), pred_box_color=(0,255, 0), img_dir='.'):
        self.vcap = cv2.VideoCapture(cam_num)
        def get_image():
            return image_from_cv(self.vcap.read)
        super().__init__(get_box_params, get_image, window_title=window_title, post_calc=post_calc,
            quit_key=quit_key, font=font, font_scale=font_scale, font_color=font_color, 
            line_type=line_type, box_thickness=box_thickness, box_color=box_color, 
            pred_box_color=pred_box_color, img_dir=img_dir)

class DrawBoundingBoxOnFolder(DrawBoundingBoxOnNext):
    def __init__(self, folder_path, get_box_params, window_title='Bounding Box', post_calc=None, quit_key='q',
        font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.5, font_color=(0,0,0), line_type=2,
        box_thickness=2, box_color=(0,0,255), pred_box_color=(0,255, 0), img_dir='.', next_key='n'):
        self.folder_path = folder_path
        get_image = None # TODO - replace with proper implementation
        super().__init__(get_box_params, get_image, window_title=window_title, post_calc=post_calc,
            quit_key=quit_key, font=font, font_scale=font_scale, font_color=font_color, 
            line_type=line_type, box_thickness=box_thickness, box_color=box_color, 
            pred_box_color=pred_box_color, img_dir=img_dir)