from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior



class SelectableRow(RecycleDataViewBehavior, BoxLayout):
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    index = None

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super().refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))

Builder.load_file(r'gui/comparator.kv')

class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout): pass

class MyRecycleView(RecycleView):
    rgrid = ObjectProperty(None)
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.data = [{'text': str(x)} for x in range(100)]

class ComparatorContentOne(BoxLayout):
    def __init__(self, popup, *args, **kwargs):
        self.popup = popup
        super().__init__(*args, **kwargs)


class ComparatorPopup(Popup):
    def __init__(self, available_tests, *args, **kwargs):
        self.available_tests = available_tests
        super().__init__(*args, **kwargs)
        self.content = ComparatorContentOne(self)
        self.title = 'Select Cell Data to Compare'
