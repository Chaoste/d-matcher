__version__ = '1.0'

import os
import trio

os.environ['KIVY_EVENTLOOP'] = 'trio'
'''trio needs to be set so that it'll be used for the event loop. '''

import kivy
import time
from concurrent.futures import ThreadPoolExecutor
kivy.require('1.0.6')

from kivy.app import App, async_runTouchApp
from kivy.clock import Clock
from kivy.properties import DictProperty
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Rectangle, Point, GraphicException
from kivy.uix.filechooser import FileChooser
from random import random
from math import sqrt

import src.d_matcher as d_matcher


class DropFile(Button):
    def __init__(self, **kwargs):
        super(DropFile, self).__init__(**kwargs)
        print('X')
        app = App.get_running_app()
        app.drops.append(self.on_dropfile)

    def on_dropfile(self, widget, filename):
        if self.collide_point(*Window.mouse_pos):
            # on_dropfile's filename is bytes (py3)
            app = App.get_running_app()
            app.root.set_input_path(filename.decode('utf-8'))


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class StatusLabel(Label):
    def set_error(self, text):
        self.color = [0.7, 0.4, 0.3, 1]
        self.text = text

    def set_warning(self, text):
        self.color = [0.9, 0.6, 0, 1]
        self.text = text

    def set_status(self, text):
        self.color = [1, 1, 1, 1]
        self.text = text

    def set_success(self, text):
        self.color = [0.3, 0.7, 0.3, 1]
        self.text = text


class DMatcher(FloatLayout):
    loadfile = ObjectProperty(None)
    input_path = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DMatcher, self).__init__(**kwargs)
        print('DMatcher init')

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
        app = App.get_running_app()
        print(f'Selected {path} as input file./')
        _, filetype = os.path.splitext(path)
        if filetype != '.csv':
            app.root.ids.label_status.set_error(f'Received invalid file of type {filetype}!')
            return

        app.root.ids.input_file_label.text = f'Selected File:\n{path}'
        app.root.ids.label_status.set_status(f'Ready to processs selected file.')
        # Set background to default behaviour (initial dark, hovered light)
        app.root.ids.drop_area.background_normal = app.root.ids.button_execute.background_normal
        app.root.ids.drop_area.background_color = [0.1, 0.4, 0.1, 1]
        app.root.ids.button_execute.background_normal = ''
        app.root.ids.button_execute.background_color = [0.1, 0.4, 0.1, 1]
        app.root.ids.button_execute.disabled = False
        self.input_path = path

    def async_execute_algorithm(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.execute_algorithm)
            # print('Future result:', future.result())

    def execute_algorithm(self):
        app = App.get_running_app()
        app.root.ids.label_result.text = 'Starting algorithm'
        d_matcher.execute(self.input_path, epochs=100, progressbar=Progressbar)
        app.root.ids.label_status.set_success(
            'Successfully created teaming files. '
            'They can be found in the same directory as the input file.')

        app.root.ids.progress_bar.value = 100


class Progressbar:
    def __init__(self, _range):
        self.app = App.get_running_app()
        self._range = _range
        self._gen = iter(_range)
        self.app.root.ids.progress_bar.value = 0

    def __next__(self):
        try:
            next_value = next(self._gen)
            new_progress_value = round(100 * next_value / len(self._range))
            if self.app.root.ids.progress_bar.value != new_progress_value:
                self.app.root.ids.progress_bar.value = new_progress_value
            return next_value
        except StopIteration:
            self.app.root.ids.progress_bar.value = 100
            raise StopIteration

    def __iter__(self):
        return self

    def set_description(self, text):
        self.app.root.ids.label_status.set_status(text)

    def set_final_desc(self, text):
        self.app.root.ids.label_result.text = text

    def refresh(self):
        # We don't need to force refreshing since kivy will take care of it
        pass


class DMatcherApp(App):
    widgets = DictProperty()
    title = 'D-Matcher'
    icon = 'icon.png'

    def __init__(self, **kwargs):
        super(DMatcherApp, self).__init__(**kwargs)
        print('Hi')

    def build(self):
        # set an empty list that will be later populated
        # with functions from widgets themselves
        self.drops = []
        print('Ho')

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



async def run_app_happily(app, nursery):
    '''This method, which runs Kivy, is run by trio as one of the coroutines.
    '''
    await async_runTouchApp(app)  # run Kivy
    print('App done')
    # now cancel all the other tasks that may be running
    nursery.cancel_scope.cancel()

def execute_algorithm():
    app = App.get_running_app()
    app.root.ids.label_result.text = 'Starting algorithm'
    d_matcher.execute(app.root.input_path, epochs=100, progressbar=Progressbar)
    app.root.ids.label_status.set_success(
        'Successfully created teaming files. '
        'They can be found in the same directory as the input file.')

    app.root.ids.progress_bar.value = 100

async def watch_button_closely(root):
    '''This is run side by side with the app and it watches and reacts to the
    button shown in kivy.'''
    i = 0

    # we watch for 7 button presses and then exit this task. if the app is
    # closed before that, run_app_happily will cancel all the tasks, so we
    # should catch it first and print it and then re-raise
    try:

        # watch the on_release event of the button and react to every release
        async for _ in root.ids.btn.async_bind('on_release'):
            execute_algorithm()
            break

        print('Goodbye :(')
    except trio.Cancelled:
        print('update_label1 canceled early')
        raise  # we MUST re-raise this exception
    finally:
        print('Done with update_label1')


if __name__ == '__main__':
    async def root_func():
        '''trio needs to run a function, so this is it. '''

        app = DMatcherApp()  # root widget
        print(app)
        print(App.get_running_app())
        # print(root)
        async with trio.open_nursery() as nursery:
            '''In trio you create a nursery, in which you schedule async
            functions to be run by the nursery simultaneously as tasks.

            This will run all three methods starting in random order
            asynchronously and then block until they are finished or canceled
            at the `with` level. '''
            nursery.start_soon(run_app_happily, app, nursery)
            # nursery.start_soon(watch_button_closely, root)

    trio.run(root_func)
    # DMatcherApp().run()
