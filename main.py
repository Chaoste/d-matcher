__version__ = '1.0'

import os
import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.properties import DictProperty
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Rectangle, Point, GraphicException
from random import random
from math import sqrt


def calculate_points(x1, y1, x2, y2, steps=5):
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt(dx * dx + dy * dy)
    if dist < steps:
        return
    o = []
    m = dist / steps
    for i in range(1, int(m)):
        mi = i / m
        lastx = x1 + dx * mi
        lasty = y1 + dy * mi
        o.extend([lastx, lasty])
    return o


class DropFile(Button):
    def __init__(self, **kwargs):
        super(DropFile, self).__init__(**kwargs)

        # get app instance to add function from widget
        app = App.get_running_app()

        # add function to the list
        app.drops.append(self.on_dropfile)

    def on_dropfile(self, widget, filename):
        # a function catching a dropped file
        # if it's dropped in the widget's area
        if self.collide_point(*Window.mouse_pos):
            # on_dropfile's filename is bytes (py3)
            app = App.get_running_app()
            app.root.set_input_path(filename.decode('utf-8'))
            # self.background_color = Color(0.4, 0.3, 1, 0.85, mode='rgba')


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class DMatcher(FloatLayout):
    loadfile = ObjectProperty(None)
    input_path = ObjectProperty(None)

    # --- FileChooser logic -------------------------------------------------- #

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        self.set_input_path(os.path.join(path, filename[0]))
        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    def set_input_path(self, path):
        print(f'Selected {path} as input file.')

        app = App.get_running_app()
        app.root.ids.input_file_label.text = f'Selected File: {path}'
        self.input_path = path

    def execute_algorithm(self):
        app = App.get_running_app()
        app.root.ids.progress_bar.value = 0
        # TODO:
        app.root.ids.label_status.text = 'Success'
        app.root.ids.progress_bar.value = 100



class DMatcherApp(App):
    widgets = DictProperty()
    title = 'D-Matcher'
    icon = 'icon.png'

    def __init__(self, **kwargs):
        super(DMatcherApp, self).__init__(**kwargs)

    def build(self):
        # set an empty list that will be later populated
        # with functions from widgets themselves
        self.drops = []

        # bind handling function to 'on_dropfile'
        Window.bind(on_dropfile=self.handledrops)

        return DMatcher()

    def handledrops(self, *args):
        # this will execute each function from list with arguments from
        # Window.on_dropfile (make sure `Window.on_dropfile` works on your system)
        for func in self.drops:
            func(*args)

    def on_pause(self):
        return True


if __name__ == '__main__':
    DMatcherApp().run()
