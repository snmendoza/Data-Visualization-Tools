
from . modchart import *
from matplotlib import pyplot as plt
import numpy as np
import pylab
from matplotlib.pyplot import cm



"""

Set up some color cycles



"""
colors_one = [cm.gist_ncar(i) for i in np.linspace(0,1,10)]

colors_two = [cm.hsv(i) for i in np.linspace(0,1,10)]

#or version 2:


class ModChartHandler(object):
    def __init__(self, tabs, app = None):

        self.ModChartLayout = ModChartLayout()
        self.tabs = tabs # these are PlotPonel items, which have .arbin_tests
        self.tests = [tab.arbin_test for tab in tabs]
        self.app = app

        self.data_tab = ModChartTab(parent=self, layout = "data_tab")
        self.statistical_tab = ModChartTab(parent=self, layout = "statistical_tab")

    def update_tests(self, tab_list):
        ## only open tests should be in the chart
        if self.tabs == tab_list:
            return
        else:
            self.tests = [tab.arbin_test for tab in tab_list]
        ## easy way is to just remake both tabs

        ## hard way is to just add new tests/remove old Tests from tabs, treeviews AND plots

        self.data_tab = ModChartTab(parent=self, layout = "data_tab")
        self.statistical_tab = ModChartTab(parent=self, layout = "statistical_tab")

    def update_legends(self, cell_test, textinput_text):
        """cell_text example:
        """
        for tab in [self.data_tab, self.statistical_tab]:
            dict = tab.lines
            dict_of_test_lines = dict[cell_test]
            for data_attr in dict_of_test_lines.keys():
                y1y2_dict = dict_of_test_lines[data_attr]
                line1 = y1y2_dict["y1"]
                line1.label = line1.create_label(mod=textinput_text)
                line1.update_visible()

                line2 = y1y2_dict["y2"]
                line2.label = line2.create_label(mod=textinput_text)
                line2.update_visible()


class ModChartTab(object):
    def __init__(self, parent = [], layout = "data_tab"):
        self.ignore_list={ "data_tab": ["Data_Point", "Date_Time", "Cycle_Index",
         "Step_Index", "ACR(Ohm)", "Internal_Resistance(Ohm)", "dV/dt(V/s)",
          "dQ/dV(Ah/V)", "dV/dQ(V/Ah)"],

        "statistical_tab":

        ["Date_Time                    ",
        "Unnamed", "V_Max_On_Cycle(V)",
        "Charge_Time(s)", "Discharge_Time(s)", "Test_Time(s)",
        "Step_Time(s)", "Current(A)","mAh/g"]

        }[layout] ### this dictionary has columnm names to ignore, depending on the type of chart it isß
        self.chart_type = layout
        self.data_type = {"data_tab": "data", "statistical_tab": "statistics"}[layout]
        self.parent = parent
        self.layout = parent.ModChartLayout.ids[layout]

        self.chart = plt.figure(figsize=(8,8))
        self.ax1 = self.chart.add_subplot(111)
        self.ax2 = self.ax1.twinx()
        #axis color scheme
        self.ax1.set_prop_cycle(color=colors_one)
        self.ax2.set_prop_cycle(color=colors_two)
        #axis legend locations
        self.ax1.legend(loc=2)
        self.ax2.legend(loc='best')



        self.lines = self.create_line_dict(data_type = self.data_type)

        self.deploy_chart()

        self.populate_treeview(self.parent.tabs)
        # self.plot_defaults()

    def update_tests(self, tabs):
        """design way to add/remove tests that have been added/removed since previous drawing of chart"""
        for tab in tabs:
            if tab in self.tabs:
                pass
            else:
                self.tabs.append(tab)

    def populate_treeview(self, tabs=None):

        tree = self.layout.ids.treeview
        for node in [i for i in tree.iterate_all_nodes()]: # necessory when rebuilding treeview
            tree.remove_node(node)
        for test in self.parent.tests:
            cell_node = TreeViewCellLabel(test=test, handler = self)
            tree.add_node(cell_node)

            for stat in test.statistics.keys():
                if stat not in self.ignore_list and "unnamed" not in stat.lower():
                    series_node = TreeViewSeriesLabel(test=test, handler = self)
                    series_node.text = stat
                    cell_node.state[stat] = {"x1":False, "y1":False, "y2":False}
                    tree.add_node(series_node, cell_node)

    def deploy_chart(self):

        self.canvas = FigureCanvasKivyAgg(self.chart, size_hint_y=0.8)
        nav_bar = CustomKivyNavBar(self.canvas, size_hint_y=0.2)

        self.layout.ids.chart_box.clear_widgets() # this is necessary when we rebuild the chart box

        self.layout.ids.chart_box.add_widget(self.canvas)
        self.layout.ids.chart_box.add_widget(nav_bar.actionbar)


    def create_line_dict(self, data_type = "statistics"):
        """
        data_type: "data" or "statistics", this function will pull
        data from test.data or test.staticsics, depending on type specified

        {test1: {"Discharge_Capacity": LineReferee1,
                "Charge_Capacity": LineReferee2},

         test2: {"Discharge_Capacity": {'y1': LineRefereey1, 'y2': LineRefereey2},
                 "Charge_Capacity": LineReferee2}
        }
        """

        if not hasattr(self, "lines"):
            lines = {}
        else:
            pass
        line_obj = {"data": LineReferee, "statistics": ScatterReferee}[data_type]
        for test in self.parent.tests:
            lines[test] = {}
            data_source = getattr(test, data_type)
            for attr in data_source.keys():
                lines[test][attr] = {"y1": line_obj(test = test, data_source = data_source, handler = self, y_stat = attr, y_axis=self.ax1),
                "y2": line_obj(test = test, data_source = data_source, handler = self, y_stat = attr, y_axis = self.ax2)}

        return lines

    # def plot_defaults(self):
    #     ### TODO find if statistical or data tab
    #     ###
    #     if self.chart_type = "data_tab":
    #         x = "test_time"
    #         y1 = "voltage"
    #     elif sef.chart_type = "statistical_tab":
    #         x1 = "cycle_index"
    #         y1 = "discharge_dapacity"
    #         y2 = "coulombic"
    #
    #     for test in self.parent.tests:


    def update_chart(self, checkbox):
        """Receive a trigger from the checkbox tree
        checkbox contains
            checkbox.axis = y1, y2 or x as string
            checkbox.group = filename (only if it is the x axis)
            checkbox.active = true or false, depeding on status
            checkbox.filename ?
        """
        test = checkbox.parent.test  #find which cell this is
        stat = checkbox.parent.text  #find which stat we need to plot
        active = checkbox.active     #get checkbox status
        axis = checkbox.axis         # get axis stringproperty from designated checkbox


        print(test, stat, active, axis)

        if "x" in checkbox.axis:
            if active:
                #x axis has been changed AND this is the "active" trigger:
                #update all of this cells lines' x_data
                print("set x axis to {}".format(stat))
                for attr in self.lines[test].keys():
                    for axis_name in self.lines[test][attr].keys():
                        LineRef = self.lines[test][attr][axis_name] # find the unique line based on stat
                        LineRef.x_attr = stat # set the attribute
                        LineRef.update_data()
                return
            else:
                return

        elif 'y' in checkbox.axis:
            LineRef = self.lines[test][stat][checkbox.axis]
            if checkbox.active and checkbox.active != LineRef.active:
                # plot!
                print('toggling')
                LineRef.active = checkbox.active
                LineRef.y_attr = stat
                LineRef.update_visible(axis=axis)

            elif checkbox.active and checkbox.active == LineRef.active:
                pass
            else:
                #not active
                LineRef.active = checkbox.active
                LineRef.update_visible(axis=axis)
        else:
            return






class LineRefBase(object):
    def __init__(self, handler = None,
    x_attr = "Cycle_Index", y_axis = None,
    y_stat = 1, active=False, test = None, data_source = None):
        self.data_source = data_source
        self.x_attr = x_attr # ie "Test_Time"
        self.y_attr = y_stat  # ie Discharge Capacity
        self.axis = y_axis #ie y1
        self.active = active #plotted or notted
        self.line = False
        self.test = test # arbin_test type
        self.handler = handler
        self.label = self.create_label()

    def create_label(self, mod = "", *args):

        title = self.test.title # file name witohout xlsx
        channel = title.split()[0]
        test_name = title.split()[1]
        stat = self.y_attr
        basic_label = "{} {} {} ({})".format(channel,mod, stat, test_name)
        return basic_label#Ch XX Discharge Capacity (Date-name)

    def update_visible(self, axis=None):
        """
        toggle between visible and invisible line, draw new line if needed
        """
        if self.active and self.line: # show existing line
            self.line.set_alpha(1)
            legend = self.label
        elif self.line and not self.active: #disable existing line
            self.line.set_alpha(0)
            legend = ""
        elif not self.line and self.active and axis:# show not existing lineif not axis
            self.update_data(axis)
            legend = self.label
        else:
            return


        self.line.set_label(legend)
        # self.handler.ax1.legend(loc='best')
        self.axis.legend()

class LineReferee(LineRefBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x_attr = "Test_Time(s)"

    def update_data(self, axis=None):
        """
        change data (mainly x data or axis y1/y2)
        """
        x_data = self.data_source[self.x_attr]
        y_data = self.data_source[self.y_attr]

        if self.active and not self.line:
            self.line, = self.axis.plot(x_data, y_data, label=self.label)
        elif not self.active and not self.line:
            return
        else:
            self.line.set_data((x_data, y_data))
        self.axis.relim()
        self.handler.ax1.relim()
        self.handler.chart.canvas.draw_idle()

class ScatterReferee(LineRefBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x_attr = "Cycle_Index"

    def update_data(self, axis=None):
        """
        change data (mainly x data or axis y1/y2)
        """
        x_data = self.data_source[self.x_attr]
        y_data = self.data_source[self.y_attr]
        data = np.column_stack((x_data,y_data))

        if self.active and not self.line:
            self.line = self.axis.scatter(x_data, y_data, label=self.label)
        elif not self.active and not self.line:
            return
        else:
            self.line.set_offsets(data)
        self.axis.relim()
        self.handler.ax1.relim()
        self.handler.chart.canvas.draw_idle()
