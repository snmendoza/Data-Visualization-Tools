from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.clock import Clock
import os

Builder.load_file(r'gui\filechooser.kv')

class LoadDialog(FloatLayout):
    "The content for a popup"
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def sort_by_date(self, names_list, filesystem):
        return sorted(names_list, key=lambda fi: os.stat(fi).st_mtime, reverse = True)

    def sort_default(self, names_list, filesystem):
        return sorted(names_list)

class FileDialog(object):
    def __init__(self, call=None):
        self.call = call
        self.block = False
    def dismiss_popup(self, *args):
        self._popup.dismiss()

    def load_file(self, directory=None):
        self.selection = None
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        if directory:
            content.ids.filechooser.path = directory
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, filename):
        if not self.block:
            self.block = True
            if self.call:
                self.call(filename)
            self.block = False
            self.dismiss_popup()
        else:
            return



class FileDialogButton(Button):
    '''
    Example on how to run
    '''
    loadfile = ObjectProperty(None)
    # savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def on_press(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            print('File Selected; {}'.format(stream))
            self.send_file()

        self.dismiss_popup()

    def send_file(self):
        pass

class FileChooserApp(App): pass

# Factory.register('FileChooserHandler', cls=FileChooserHandler)
# Factory.register('LoadDialog', cls=LoadDialog)

if __name__ == '__main__':

    FileChooserApp().run()
