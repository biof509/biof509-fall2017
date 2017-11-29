from shapely.geometry import LineString, box
from shapely.ops import transform
from shapely.wkt import dumps, loads
import json


class LabelLayer(object):


    def __init__(self, image, filename):
        # Get unique identifier from image
        self.image = image
        try:
            f = open('{0}.json'.format(self.image.hash), 'r')
            labels = json.load(f)
            f.close()
            self.labels = [loads(i) for i in labels]
        except:
            self.labels = []

            
    def get_region(self, x, y, level, width=600, height=600):
        # First filter all labels to those within the region
        maxx = x + width * self.image.level_downsamples[level]
        maxy = y + height * self.image.level_downsamples[level]
        bbox = box(x, y, maxx, maxy)
        bbox_labels = [i for i in self.labels if bbox.intersects(i)]
        # Transform coordinates to be in the display coordinates
        def scale_down(oldx, oldy):
            newx = (oldx - x) / self.image.level_downsamples[level]
            newy = (oldy - y) / self.image.level_downsamples[level]
            return (newx, newy)
        bbox_labels = [transform(scale_down, i) for i in bbox_labels]
        return bbox_labels


    def add_label(self, label, radius):
        new_label = LineString(label).buffer(radius)
        new_label = new_label.simplify(1)
        intersecting_labels = [i for i in self.labels if new_label.intersects(i)]
        for i in intersecting_labels:
            new_label = new_label.union(i)
            self.labels.remove(i)
        self.labels.append(new_label)


    def remove_label(self, label, radius):
        label_to_remove = LineString(label).buffer(radius)
        label_to_remove = label_to_remove.simplify(1)
        intersecting_labels = [i for i in self.labels if label_to_remove.intersects(i)]
        new_labels = []
        for i in intersecting_labels:
            new_label = i.difference(label_to_remove)
            new_labels.append(new_label)
            self.labels.remove(i)
        self.labels.extend(new_labels)


    def save(self):
        with open('{0}.json'.format(self.image.hash), 'w+') as f:
            labels = [dumps(i) for i in self.labels]
            json.dump(labels, f)


