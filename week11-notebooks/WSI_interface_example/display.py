import sys
import tkinter as tk
from tkinter import filedialog as tkFileDialog
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from descartes.patch import PolygonPatch

from image import Image
from labellayer import LabelLayer





class Display(tk.Tk):


    step_size = 0.5

    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Glomeruli labeling")
        self.container = tk.Frame(self)
        self._open_file()
        self._create_interface()
        self._create_main_pane()
        self.interface.grid(row=0, column=1, sticky='ne')
        self.main_pane.get_tk_widget().grid(row=0, column=0, rowspan=2, 
                sticky='nsew')
        self.button_pressed = False
    
    
    def _create_interface(self):
        self.interface = tk.Frame(self)
        self.interface.columnconfigure(0, minsize=100)
        self.interface.columnconfigure(1, minsize=100)
        finish_button = tk.Button(self.interface, text="Finish",
                                    command=self.finish)
        finish_button.grid(row=0, column=0, columnspan=2, sticky='we')
        zoom_in_button = tk.Button(self.interface, text="Zoom in",
                                    command=self.zoom_in)
        zoom_in_button.grid(row=1, column=0, sticky='we')
        zoom_out_button = tk.Button(self.interface, text="Zoom out",
                                    command=self.zoom_out)
        zoom_out_button.grid(row=1, column=1, sticky='we')
        up_button = tk.Button(self.interface, text="Up",
                                    command=self.up)
        up_button.grid(row=2, column=0, columnspan=2, sticky='we')
        left_button = tk.Button(self.interface, text="Left",
                                    command=self.left)
        left_button.grid(row=3, column=0, sticky='we')
        right_button = tk.Button(self.interface, text="Right",
                                    command=self.right)
        right_button.grid(row=3, column=1, sticky='we')
        down_button = tk.Button(self.interface, text="Down",
                                    command=self.down)
        down_button.grid(row=4, column=0, columnspan=2, sticky='we')
        add_button = tk.Button(self.interface, text="Add label",
                                    command=self.add_label)
        add_button.grid(row=5, column=0, sticky='we')
        remove_button = tk.Button(self.interface, text="Remove label",
                                    command=self.remove_label)
        remove_button.grid(row=5, column=1, sticky='we')
        

    def _create_main_pane(self):
        self.main_pane_f = mpl.figure.Figure(figsize=(8,8))
        self.main_pane_ax = self.main_pane_f.add_subplot(111)
        self.main_pane_ax.imshow(self.image.get_region(0,0,
            self.image.level_count-1))
        labels = self.label_layer.get_region(0,0, self.image.level_count-1)
        for label in labels:
            patch = PolygonPatch(label, 
                    facecolor='red', edgecolor='red', alpha=0.5)
            self.main_pane_ax.add_patch(patch)
        self.main_pane = FigureCanvasTkAgg(self.main_pane_f, self)
        self.main_pane.show()
        self.current = {'x': 0, 'y': 0, 
                'zoom': self.image.level_count-1,
                'window_width': 600,
                'window_height': 600,}
        self.cursor_loc = (300,300)
        self.cursor_patch = mpl.patches.Circle(self.cursor_loc,
                radius = int(50 / 1.5 ** self.current['zoom']), edgecolor='green',
                facecolor='green', alpha=0.5)
        self.main_pane_ax.add_patch(self.cursor_patch)
        self.label_state = 'Add'
        self.main_pane.mpl_connect('motion_notify_event', self._cursor_move)
        self.main_pane.mpl_connect('motion_notify_event', self._cursor_draw)
        self.main_pane.mpl_connect('button_press_event', self._cursor_draw)
        self.main_pane.mpl_connect('button_release_event', self._cursor_draw)


    def _open_file(self):
        """Prompt the user for an image to work with"""
        self.filename = tkFileDialog.askopenfilename()
        # Open file
        self.image = Image(self.filename)
        # Create labeling layer
        self.label_layer = LabelLayer(self.image, self.filename)
        
        
    def finish(self):
        self.label_layer.save()
        
        
    def add_label(self):
        self.label_state = 'Add'
        self.cursor_patch.set_color('green')
        self.main_pane.draw()
    
    
    def remove_label(self):
        self.label_state = 'Remove'
        self.cursor_patch.set_color('red')
        self.main_pane.draw()

        
    def right(self):
        x = self.current['x'] + self.step_size * self.current['window_width'] * \
                2 ** (self.current['zoom'] - 1)
        self._change_focus(x, self.current['y'], self.current['zoom'])

        
    def left(self):
        x = self.current['x'] - self.step_size * self.current['window_width'] * \
                2 ** (self.current['zoom'] - 1)
        self._change_focus(x, self.current['y'], self.current['zoom'])

        
    def up(self):
        y = self.current['y'] - self.step_size * self.current['window_height'] * \
                2 ** (self.current['zoom'] - 1)
        self._change_focus(self.current['x'], y, self.current['zoom'])

        
    def down(self):
        y = self.current['y'] + self.step_size * self.current['window_height'] * \
                2 ** (self.current['zoom'] - 1)
        self._change_focus(self.current['x'], y, self.current['zoom'])

        
    def zoom_in(self):
        x = self.current['x'] + 2 ** (self.current['zoom'] - 1) \
                * self.current['window_width'] / 2
        y = self.current['y'] + 2 ** (self.current['zoom'] - 1) \
                * self.current['window_height'] / 2
        self._change_focus(x, y, 
                self.current['zoom'] - 1)

                
    def zoom_out(self):
        x = self.current['x'] - 2 ** self.current['zoom'] \
                * self.current['window_width'] / 2
        y = self.current['y'] - 2 ** self.current['zoom'] \
                * self.current['window_height'] / 2
        self._change_focus(x, y, 
                self.current['zoom'] + 1)


    def _change_focus(self, x, y, zoom):
        window_width = self.current['window_width']
        window_height = self.current['window_height']
        width = self.image.dimensions0[0]
        height = self.image.dimensions0[1]
        if x < 0:
            x = 0
        if (x + window_width) > width:
            x = width - window_width
        if y < 0:
            y = 0
        if (y + window_height) > height:
            y = height - window_height
        if zoom > (self.image.level_count - 1):
            zoom = self.image.level_count - 1
        if zoom < 0:
            zoom = 0
        self.main_pane_ax.clear()
        image_region = self.image.get_region(int(x), int(y), zoom)
        self.main_pane_ax.imshow(image_region)
        labels = self.label_layer.get_region(x, y, zoom)
        for label in labels:
            patch = PolygonPatch(label,
                    facecolor='green', edgecolor='green', alpha=0.5)
            self.main_pane_ax.add_patch(patch)
        self.cursor_patch.set_radius(50 / 1.5 ** zoom)
        self.main_pane_ax.add_patch(self.cursor_patch)
        self.main_pane.draw()
        self.current['x'] = x
        self.current['y'] = y
        self.current['zoom'] = zoom
        self.current['window_width'] = 600
        self.current['window_height'] = 600


    def _cursor_move(self, event):
        if not event.inaxes:
            return
        x, y = event.xdata, event.ydata
        self.cursor_patch.center = (x,y)
        self.main_pane.draw()


    def _cursor_draw(self, event):
        if event.name == 'button_press_event':
            self.new_label = [(event.xdata, event.ydata)]
            self.button_pressed = True
        elif self.button_pressed and (event.name == 'motion_notify_event'):
            self.new_label.append((event.xdata, event.ydata))
        elif self.button_pressed and (event.name == 'button_release_event'):
            self.button_pressed = False
            label = [(self.current['x'] + i[0] * self.image.level_downsamples[self.current['zoom']],
                self.current['y'] + i[1] * self.image.level_downsamples[self.current['zoom']]) \
                for i in self.new_label]
            radius = self.image.level_downsamples[self.current['zoom']] * \
                            50 / 1.5 ** self.current['zoom']
            if self.label_state == 'Add':
            	self.label_layer.add_label(label, radius = radius)
            else:
            	self.label_layer.remove_label(label, radius = radius)
        else:
            return






