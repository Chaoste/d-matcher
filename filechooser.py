from kivy.app import App
from kivy.garden.filebrowser import FileBrowser
from os.path import sep, expanduser, isdir, dirname
from kivy.utils import platform


class TestApp(App):
    def build(self):
        print('X')
        if platform == 'win':
            user_path = dirname(expanduser('~')) + sep + 'Documents'
        else:
            user_path = expanduser('~') + sep + 'Documents'
        browser = FileBrowser(select_string='Select',
                              favorites=[(user_path, 'Documents')])
        browser.bind(on_success=self._fbrowser_success,
                     on_canceled=self._fbrowser_canceled)
        print('Y')
        return browser
    def _fbrowser_canceled(self, instance):
        print('cancelled, Close self.')
    def _fbrowser_success(self, instance):
        print(instance.selection)

TestApp().run()
