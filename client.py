__version__ = '1.0'

import traceback
import os
import trio

os.environ['KIVY_EVENTLOOP'] = 'trio'
'''trio needs to be set so that it'll be used for the event loop. '''

import kivy
import threading
kivy.require('1.0.6')

# Disable multitouch - otherwise there's a red dot visible to the user
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.properties import DictProperty
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

from utils import mac_notify

import src.d_matcher as d_matcher

# easy takes ~3 minutes, medium 7 minutes, hard >10 minutes
DIFFICULTIES = {
    'debug': {
        'epochs': 1,
        'mutation_intensity': 1
    },
    'easy': {
        'epochs': 50,
        'mutation_intensity': 10
    },
    'medium': {
        'epochs': 100,
        'mutation_intensity': 20
    },
    'hard': {
        'epochs': 150,
        'mutation_intensity': 40
    },
}


class DropFile(Button):
    def __init__(self, **kwargs):
        super(DropFile, self).__init__(**kwargs)
        app = App.get_running_app()
        app.drops.append(self.on_dropfile)

    def on_dropfile(self, widget, filename):
        # print(widget, filename, Window.mouse_pos, self.pos, self.size, self.collide_point(*Window.mouse_pos))
        # if self.collide_point(*Window.mouse_pos):
        # on_dropfile's filename is bytes (py3)
        app = App.get_running_app()
        app.root.set_input_path(filename.decode('utf-8'))


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40:  # 40 - Enter key pressed
            filechooser = self.ids.filechooser
            if filechooser.path and filechooser.selection:
                self.load(filechooser.path, filechooser.selection)
        else:
            print("Unknown keycode", keycode)


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


class Progressbar:
    def __init__(self, _range):
        self.app = App.get_running_app()
        self._range = _range
        self._gen = iter(_range)
        self.first_value = self.app.root.dmatcher_runs * 20
        self.last_value = self.first_value + 20
        self.app.root.ids.progress_bar.value = self.first_value


    def __next__(self):
        try:
            next_value = next(self._gen)
            new_progress_value = self.first_value + round(20 * next_value / len(self._range))
            if self.app.root.ids.progress_bar.value != new_progress_value:
                self.app.root.ids.progress_bar.value = new_progress_value
            return next_value
        except StopIteration:
            self.app.root.ids.progress_bar.value = self.last_value
            raise StopIteration

    def __iter__(self):
        return self

    def set_description(self, text):
        self.app.root.ids.label_status.set_status(f'Teaming {self.app.root.dmatcher_runs+1}: {text}')

    def set_final_desc(self, text):
        self.app.root.ids.label_result.set_success(f'Teaming {self.app.root.dmatcher_runs+1}:\n{text}')
        self.app.root.dmatcher_runs += 1


    def refresh(self):
        # We don't need to force refreshing since kivy will take care of it
        pass


class DMatcher(FloatLayout):
    input_path = ObjectProperty(None)
    difficulty = ObjectProperty(None)
    dmatcher_runs = ObjectProperty(0)

    def __init__(self, **kwargs):
        super(DMatcher, self).__init__(**kwargs)
        self.init_async_listener()

    # --- FileChooser logic -------------------------------------------------- #

    def show_error(self, error):
        print(error)
        app = App.get_running_app()
        self._error_popup = Popup(
            title="Error occurred", size_hint=(0.8, 0.4),
            content=Label(text=error, halign="center"))
        self._error_popup.bind(on_dismiss=app.stop)
        self._error_popup.open()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        self.set_input_path(os.path.join(path, filename[0]))
        self.dismiss_popup()

    def on_change_difficulty(self, value):
        if value == -1:
            level = 'Short'
            self.difficulty = 'easy'
        if value == 0:
            level = 'Medium'
            self.difficulty = 'medium'
        if value == 1:
            level = 'Long'
            self.difficulty = 'hard'
        self.ids.label_difficulty.text = f'Processing Timg: {level}'


    def dismiss_popup(self):
        self._popup.dismiss()
        Window.unbind(on_key_down=self._popup.content._on_keyboard_down)

    def set_input_path(self, path):
        app = App.get_running_app()
        _, filetype = os.path.splitext(path)
        if filetype != '.csv' and filetype != '.xlsx':
            app.root.ids.label_status.set_error(f'Received invalid file of type {filetype}!')
            return

        app.root.ids.label_input_file.text = f'Selected File:\n{path}'
        app.root.ids.label_status.set_status(f'Ready to processs selected file.')
        # Set background to default behaviour (initial dark, hovered light)
        app.root.ids.button_input_file.background_normal = app.root.ids.button_execute.background_normal
        app.root.ids.button_input_file.background_color = [0.1, 0.4, 0.1, 1]
        app.root.ids.button_execute.disabled = False
        self.input_path = path

    def init_async_listener(self):
        thread = threading.Thread(target=lambda: trio.run(init_async_listener))
        thread.start()


class DMatcherApp(App):
    widgets = DictProperty()
    title = 'D-Matcher'
    icon = 'res/favicon-v2.ico'

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


async def init_async_listener():
    '''This method is also run by trio and periodically prints something.'''
    app = App.get_running_app()
    async with trio.open_nursery() as nursery:
        nursery.start_soon(watch_ondrop_closely, app)
        nursery.start_soon(watch_button_closely, app)

        async for _ in app.async_bind(
                'on_stop', thread_fn=trio.BlockingTrioPortal().run_sync):
            break
        nursery.cancel_scope.cancel()


async def watch_ondrop_closely(app):
    async for args in Window.async_bind(
            'on_dropfile', thread_fn=trio.BlockingTrioPortal().run_sync):
        app.handledrops(*args)


async def watch_button_closely(app):
    '''This method is also run by trio and watches and reacts to the button
    shown in kivy.'''
    root = app.root
    if root is None:
        return

    # watch the on_release event of the button and react to every release
    async for _ in root.ids.button_execute.async_bind(
            'on_release', thread_fn=trio.BlockingTrioPortal().run_sync):
        app.root.ids.slider_difficulty.disabled = True
        app.root.ids.button_input_file.disabled = True
        app.root.ids.button_execute.disabled = True
        input_path = app.root.input_path
        app.root.dmatcher_runs = 0
        execute_algorithm(app, input_path)
        app.root.ids.slider_difficulty.disabled = False
        app.root.ids.button_execute.disabled = False
        app.root.ids.button_input_file.disabled = False


def execute_algorithm(app, input_path):
    app.root.ids.label_result.set_status('Creating 5 different teamings...')
    app.root.ids.label_status.set_status('')
    try:
        epochs=DIFFICULTIES[app.root.difficulty]['epochs']
        mutation_intensity=DIFFICULTIES[app.root.difficulty]['mutation_intensity']
        teaming = d_matcher.execute(
            input_path, epochs=epochs, mutation_intensity=mutation_intensity,
            progressbar=Progressbar, amount_teamings=3)
        n_collisions = len(list(get_collisions(teaming)))
        app.root.ids.button_execute.text = 'Regenerate Teaming'
        app.root.ids.label_status.set_success(f'Collisions: {n_collisions}')
        app.root.ids.label_result.set_success(
            'Successfully created teaming files. '
            'They can be found in the same directory as the input file.')
        mac_notify("D-Matcher is done", "Successfully created teaming files. They "
            "can be found in the same directory as the input file.")
        app.root.ids.progress_bar.value = 100
    except BaseException as e:
        if not isinstance(e, KeyboardInterrupt):
            app.root.show_error(
                f"An error occurred during execution:\n{repr(e)}\n\n"
                f"For more information see \n{os.path.abspath('./error.txt')}"
            )
            error_path = os.path.join(os.path.dirname(input_path), 'error.txt')
            with open(error_path, 'a') as file:
                file.write(f'{repr(e)}: {e.__doc__}\n\n')
                file.write(traceback.format_exc())
                file.write('\n\n\n')


if __name__ == '__main__':
    try:
        DMatcherApp().run()
    except trio.RunFinishedError:
        # Called when error popup closes the application
        pass
