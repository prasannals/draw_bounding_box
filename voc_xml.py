from lxml import etree

def single_element(elename, text):
    ele = etree.Element(elename)
    ele.text= text
    return ele

def bndbox(xmin, ymin, xmax, ymax):
    bbox = etree.Element('bndbox')
    children = [single_element('xmin', str(xmin)),
               single_element('ymin', str(ymin) ),
               single_element('xmax', str(xmax) ),
               single_element('ymax', str(ymax) )]
    for child in children:
        bbox.append(child)
    return bbox

def object_xml(name, xmin, ymin, xmax, ymax, 
    pose='Unspecified', truncated=0, difficult=0):
    obj = etree.Element('object')
    children = [single_element('name', name), 
                single_element('pose', pose),
               single_element('truncated', str(truncated)),
               single_element('difficult', str(difficult)),
               bndbox(xmin, ymin, xmax, ymax)]
    for child in children:
        obj.append(child)
    return obj

def annotation(folder, filename, path, width, height, depth, 
               objects ,segmented=0):
    '''
    objects - a list of xml elements representing objects (use "object_xml" function)
    '''
    root = etree.Element('annotation')
    children = ([single_element('folder', folder),
               single_element('filename', filename),
               single_element('path', path),
               single_element('width', str(width)),
               single_element('height', str(height)),
               single_element('depth', str(depth))] + objects)
    for child in children:
        root.append(child)
    return root

class VOCAnnotation():
    def __init__(self, folder, filename, path, width, height, depth):
        self.folder, self.filename, self.path = folder, filename, path
        self.width, self.height, self.depth = width, height, depth
        self.objects = []
        
    def add_object(self, obj):
        self.objects.append(obj)
    
    def get_xml_string(self):
        xml = annotation(self.folder, self.filename, self.path, 
           self.width, self.height, self.depth, self.objects)
        return etree.tostring(xml, pretty_print=True).decode('ascii')
    
    def write_to_file(self, path):
        with open(path, 'w') as f:
            f.write(self.get_xml_string())

def pprint_xml(ele):
    print(etree.tostring(ele, pretty_print=True).decode('ascii'))

# objs = [object_xml('sports_car',10, 20, 35, 25), 
#        object_xml('jeep',100, 120, 235, 125),
#        object_xml('bus',10, 12, 23, 15)]
# voc = annotation('c', 'vehicles.jpg', '/home/user/vehicles.jpg', 
#            1920, 1080, 3, objs)
# pprint_xml(voc)

# voc = VOCAnnotation('c', 'vehicles.jpg', '/home/user/vehicles.jpg', 1920, 1080, 3)
# voc.add_object(object_xml('sports_car',10, 20, 35, 25))
# voc.add_object(object_xml('jeep',100, 120, 235, 125))
# voc.add_object(object_xml('bus',10, 12, 23, 15))
# print(voc.get_xml_string())