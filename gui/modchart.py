from kivy.uix.splitter import Splitter
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.treeview import TreeViewNode, TreeViewLabel, TreeView
from kivy.properties import StringProperty
from kivy.garden.matplotlib.backend_kivy import FigureCanvas
from . menu_definitions import *
Builder.load_file(r'gui/modchart.kv')


class TreeViewLabel(Label, TreeViewNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TreeViewCellLabel(BoxLayout, TreeViewNode):
    text = StringProperty("A")
    def __init__(self, test=None, handler = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test = test
        self.handler = handler.parent #parent is the actual "handler"
        self.text = self.test.filename
        self.state = {}

    def update_legend_text(self, textinput):
        """respond to a change in the checked boxes"""
        self.handler.update_legends(self.test, textinput.text)

class TreeViewSeriesLabel(BoxLayout, TreeViewNode):
    filename = StringProperty("A")
    text = StringProperty("A")
    axis = StringProperty("")

    def __init__(self, test=None, handler = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = handler
        self.test = test
        self.filename = test.filename

    def trigger_update(self, checkbox):
        """respond to a change in the checked boxes"""
        self.handler.update_chart(checkbox)

class ModChartLayout(TabbedPanel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ModChartTab(TabbedPanelItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == "__main__":
    class GUITestApp(App):
        def build(self):
            self.main_layout  = ModChartLayout()

            return self.main_layout


    app = GUITestApp()
    app.run()
