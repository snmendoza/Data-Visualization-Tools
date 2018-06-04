from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

Builder.load_file(r'gui\comparator.kv')

class ComparatorContent(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ComparatorPopup(Popup):
    def __init__(self, *args, **kwargs):
        self.content = ComparatorContent()
        super().__init__(*args, **kwargs)
