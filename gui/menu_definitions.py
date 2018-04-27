'''
Collection of python-defined GUI objects and their functionality
corresponding .kv file contains graphical setup and descriptions.
'''

### properties
from kivy.properties import ObjectProperty
###
from kivy.lang import Builder
from kivy.clock import Clock
from kivy._clock import ClockEvent
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.treeview import TreeViewNode, TreeViewLabel, TreeView
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem, TabbedPanelHeader
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas,\
                                                NavigationToolbar2Kivy

from functools import partial
from time import time
from os import startfile
import configuration
from matplotlib import pyplot as plt

Builder.load_file(r'gui\menu_definitions.kv')

class MenuBar(BoxLayout):
    scrolltree = ObjectProperty(None)

class PlotTabbedPanel(TabbedPanel): pass

class CustomKivyNavBar(NavigationToolbar2Kivy):
   def drag_pan(self, event):
        """Callback for dragging in pan/zoom mode.
        copied from matplotlib docs, overriding
        the canvas draw to make faster panning"""
        for a, ind in self._xypress:
            #safer to use the recorded button at the press than current button:
            #multiple button can get pressed during motion...
            a.drag_pan(self._button_pressed, event.key, event.x, event.y)
        # self.canvas.draw_idle()
        self.canvas.draw()

class PlotTab(BoxLayout):
    def __init__(self, actual_parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actual_parent = actual_parent

class CloseableHeaderOverLay(BoxLayout):
    def __init__(self, parent, *args, **kwargs):
        self.apparent = parent
        super().__init__(*args, **kwargs)


class PlotPanelItem(TabbedPanelItem):
    def __init__(self, plot_handler, arbin_test,root=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        TabbedPanelHeader.add_widget(self, CloseableHeaderOverLay(self))
        ### input parameters
        self.plot_handler = plot_handler
        self.arbin_test = arbin_test
        self.root = root

        ### get items to create plot tab
        figure = self.plot_handler.figure
        self.figure = figure
        canvas = FigureCanvas(figure)

        ### define plot tab and add to self
        self.plot_tab = PlotTab(actual_parent = self)
        self.plot_tab.add_widget(canvas)
        self.add_widget(self.plot_tab)
        if self.arbin_test.cell_build_info is not None:
            mass_header = configuration.parser['settings']['mass_header']
            mass = self.arbin_test.cell_build_info[mass_header]
            self.plot_tab.ids.mass_input.text = str(mass)

        ### get my nav bar
        # self.nav_bar = NavigationToolbar2Kivy(canvas)
        self.nav_bar = CustomKivyNavBar(canvas)
        try:
            setattr(self.nav_bar.actionbar,'background_image', '')
            setattr(self.nav_bar.actionbar,'background_color', (.5, .47, .5, 0.7))
        except Exception as e:
            print(e)
        self.plt_canvas = canvas

    def add_widget(self, widget, index=0):
        self.content = widget
        if not self.parent:
            return
        panel = self.parent.tabbed_panel
        if panel.current_tab == self:
            panel.switch_to(self)

    def remove_widget(self, widget):
        self.content = None
        if not self.parent:
            return
        panel = self.parent.tabbed_panel
        if panel.current_tab == self:
            panel.remove_widget(widget)

    def on_release(self, *largs):
        # Tabbed panel header is a child of tab_strib which has a
        # `tabbed_panel` property
        if self.parent:
            self.parent.tabbed_panel.switch_to(self)
            if self.root:
                self.root.ids.nav_bar.clear_widgets()
                self.root.ids.nav_bar.add_widget(self.nav_bar.actionbar)
        else:
            # tab removed before we could switch to it. Switch back to
            # previous tab

            self.panel.switch_to(self.panel.current_tab)

    def update_mass(self, instance):
        '''
        convert plot from mAh to mAh/g
        intakes a TextInput (mass in milligrams), outputs nothing
        '''
        try:
            mass = float(instance.text) / 1000
        except Exception as e:
            print('error converting mass input to float\n', instance.text, e)
            return

        # recalculate arbin test with numbers
        q_plot = self.plot_handler.ax2
        new_qc = self.arbin_test.statistics['Charge_Capacity(Ah)'] * 1000 / mass
        new_qd = self.arbin_test.statistics['Discharge_Capacity(Ah)'] * 1000 / mass

        # change the plot data
        self.arbin_test.qc_plot.set_ydata(new_qc)
        self.arbin_test.qd_plot.set_ydata(new_qd)

        self.plot_handler.ax2.relim()
        self.plot_handler.ax2.autoscale(enable=True, axis='y')
        self.plot_handler.ax2.set_ylabel('Capacity (mAh/g)')

        self.plt_canvas.draw()

    def launch_excel(self, instance, *args):
        '''
        Launch one or all corresponding excel files being displayed in this tab
        '''
        try:
            excel_file = self.arbin_test.source.io
            startfile(excel_file)
        except Exception as e:
            print('failed to launch excel file {} : \n'.format(excel_file), e)

    def update_reference(self, instance, *args):
        '''
        Add a milestone reference line to the capacity plot or update if not present
        '''
        try:
            target = float(instance.text)
        except Exception as e:
            print('error converting mass input to float\n', instance.text, e)
            return

        if not int(target):
            self.plot_handler.ref_line.set_color('white')
            self.plot_handler.ref_line.set_label(None)
            print('set')
        else:
            ref_new = [target, target]
            self.plot_handler.ref_line.set_ydata(ref_new)
            self.plot_handler.ref_line.set_label('Milestone')
            self.plot_handler.ref_line.set_color('grey')
        self.plt_canvas.draw()
        return True

    def clear(self, *args):
        plt.close(self.figure)



class ScrollTree(ScrollView):
    treeview = ObjectProperty(None)


class TreeViewButton(Label, TreeViewNode): pass

class ActiveTreeViewLabel(TreeViewLabel):
    node_object = ObjectProperty(None)

class CustomTreeView(TreeView):
    scheduled_touch_down = None
    app = ObjectProperty(None)

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            self.app.plot_selected()
        else:
            node = self.get_node_at_pos(touch.pos)
            print(node)
            if not node:
                return
            if node.disabled:
                return
            # toggle node or selection ?
            if node.x - self.indent_start <= touch.x < node.x:
                self.toggle_node(node)
            elif node.x <= touch.x:
                self.select_node(node)
                node.dispatch('on_touch_down', touch)
            return True



class Root(BoxLayout):
    menubar = ObjectProperty(None)
    plotWindow = ObjectProperty(None)
