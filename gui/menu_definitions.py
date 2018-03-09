'''
Collection of python-defined GUI objects and their functionality
corresponding .kv file contains graphical setup and descriptions.
'''

### properties
from kivy.properties import ObjectProperty
###
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.treeview import TreeViewNode, TreeViewLabel
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem, TabbedPanelHeader
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas,\
                                                NavigationToolbar2Kivy

class MenuBar(BoxLayout):
    scrolltree = ObjectProperty(None)

class PlotTabbedPanel(TabbedPanel): pass

class PlotTab(BoxLayout):
    def __init__(self, actual_parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actual_parent = actual_parent

class PlotPanelItem(TabbedPanelItem):
    def __init__(self, plot_handler, arbin_test,root=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ### input parameters
        self.plot_handler = plot_handler
        self.arbin_test = arbin_test
        self.root = root

        ### get items to create plot tab
        figure = self.plot_handler.figure
        canvas = FigureCanvas(figure)

        ### define plot tab and add to self
        self.plot_tab = PlotTab(actual_parent = self)
        self.plot_tab.add_widget(canvas)
        self.add_widget(self.plot_tab)

        ### get my nav bar
        self.nav_bar = NavigationToolbar2Kivy(canvas)
        self.plt_canvas = canvas

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



class ScrollTree(ScrollView):
    treeview = ObjectProperty(None)


class TreeViewButton(Label, TreeViewNode): pass

class ActiveTreeViewLabel(TreeViewLabel):
    node_object = ObjectProperty(None)

class Root(BoxLayout):
    menubar = ObjectProperty(None)
    plotWindow = ObjectProperty(None)
