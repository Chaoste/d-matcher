__version__ = '1.0'

import os
import trio

os.environ['KIVY_EVENTLOOP'] = 'trio'
'''trio needs to be set so that it'll be used for the event loop. '''

import kivy
import threading
kivy.require('1.0.6')

from kivy.app import App
from kivy.properties import DictProperty
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.utils import trio_run_in_kivy_thread

import src.d_matcher as d_matcher


class DropFile(Button):
    def __init__(self, **kwargs):
        super(DropFile, self).__init__(**kwargs)
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
        self.init_async_listener()

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

    def init_async_listener(self):
        thread = threading.Thread(target=self.thread_fn)
        thread.start()

    # def async_execute_algorithm(self):
    #     with ThreadPoolExecutor(max_workers=1) as executor:
    #         call = executor.submit(self.execute_algorithm)
    #         call.result()

    def thread_fn(self):
        app = App.get_running_app()
        trio.run(init_async_listener, app)


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


async def init_async_listener(app):
    '''This method is also run by trio and periodically prints something.'''
    async with trio.open_nursery() as nursery:
        nursery.start_soon(watch_button_closely, app)

        async for _ in app.async_bind(
                'on_stop', thread_fn=trio.BlockingTrioPortal().run_sync):
            break
        nursery.cancel_scope.cancel()


async def watch_button_closely(app):
    '''This method is also run by trio and watches and reacts to the button
    shown in kivy.'''
    root = app.root

    # watch the on_release event of the button and react to every release
    async for _ in root.ids.button_execute.async_bind(
            'on_release', thread_fn=trio.BlockingTrioPortal().run_sync):
        input_path = app.root.input_path
        await trio_run_in_kivy_thread(
            execute_algorithm, app, input_path)


def execute_algorithm(app, input_path):
    app.root.ids.label_result.text = 'Starting algorithm'
    d_matcher.execute(
        input_path, epochs=100, progressbar=Progressbar)
    app.root.ids.label_status.set_success(
        'Successfully created teaming files. '
        'They can be found in the same directory as the input file.')

    app.root.ids.progress_bar.value = 100

if __name__ == '__main__':
    DMatcherApp().run()
