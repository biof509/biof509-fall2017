import os
from openslide import OpenSlide, open_slide, PROPERTY_NAME_QUICKHASH1

class Image(object):


    def __init__(self, image_filename):
        print(image_filename)
        self.slide = open_slide(image_filename)
        self.dimensions0 = self.slide.dimensions
        self.level_count = self.slide.level_count
        self.hash = self.slide.properties[PROPERTY_NAME_QUICKHASH1]
        self.level_downsamples = self.slide.level_downsamples

        
    def get_region(self, x, y, level, width=600, height=600):
        return self.slide.read_region((x, y), level, (width,height))

        
    def get_thumbnail(self, max_width=100, max_height=100):
        return self.slide.get_thumbnail((max_width, max_height))

