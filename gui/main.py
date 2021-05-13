## pre-configuration
import kivy
kivy.require('1.10.0')
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '1100')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy','exit_on_escape', 0)
##
## module imports
import multiprocessing
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.popup import Popup
from os.path import basename
import matplotlib
from collections import OrderedDict as OrDict
import traceback
##
## local imports
from . menu_definitions import * # custom kivy nav bar
from . comparator import *
from utils import file_utils
#import kivy.garden.contextmenu
from . import filechooser
##
## setup
# matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from kivy.garden.matplotlib.backend_kivy import FigureCanvas
import numpy as np
##

class Root(FloatLayout): pass

class DataApp(App):

    def build(self, control_module = None):
        Window.bind(on_key_down=self.key_down_action)
        self.root = Root()
        self.icon = 'icon.png'

        ### generate important references ##
        # plotting module
        if control_module:
            self.data_plot = control_module
        # file tree
        # self.file_tree = self.root.ids.menubar.ids.scrolltree.ids.treeview
        self.plotted_files = []
        self.added_files = []
        #plotting area
        self.plot_panel = self.root.ids.PlotPanel
        self.OSManager = file_utils.OSfacade()
        return self.root

    def load_active_workbook(self, *args):
        popup_label = Label(text='Opening File...')
        popup = Popup(title='Loading', content=popup_label, auto_dismiss=False)
        popup.open()
        try:
            popup_label.text = 'Getting Workbook name'
            ## Windows code
            print("test")
            wb = self.OSManager.get_active_excel()

            popup_label.text = 'Loading Data...'
            self.load_data_file([wb])
            popup_label.text = 'Done'
        except Exception as e:
            popup_label.text = 'Failed: {}'.format(e)
            print('Failed to retrieve active excel workbook', e, traceback.print_exc())
            popup.auto_dismiss = True
        else:
            popup.dismiss()

    def load_data_file(self, file_list):
        '''
        Compatibility check for files that are to be added to the tree view
        file_list should simply be a list of files -  but it is a kivy observable list,
        not an actual list apparently
        '''
        pyplot_handler = self.control_module.PyPlotHandler
        ArbinTest = self.control_module.ArbinTest

        if type(file_list) is not list:
            file_list = [file_list]
        print('File imported: \n{}'.format(file_list))

        try: # catch iteration error
            for file in file_list:
                test_map = self.control_module.test_mapper.generate_data_mapping(file)
                tests = self.control_module.test_mapper.generate_arbin_tests(test_map)

                for arbin_test in tests:

                    # create plot handler from arbin test
                    test_plot_handler = pyplot_handler(arbin_test, types=ArbinTest)

                    # create canvas and navigation tools, populate layout
                    self.generate_plot_tab(test_plot_handler, arbin_test)
        except Exception as e:
            print(e)
            traceback.print_exc()
        else:
            print("loaded data file {}".format(file_list))

    def generate_plot_tab(self, plot_handler, arbin_test):
        '''
        Takes in figure and generates a plot tab, adds tab to the plot panel
        '''
        print('generate plot tab')
        ### send signal to generate plots
        plot_handler.create_plots()
        ### create custom plot tab
        new_tab = PlotPanelItem(plot_handler, arbin_test,root=self.root, text='{} (Ch. {})'.format(arbin_test.item_ID, arbin_test.arbin_ID))
        ### add tab to tabbed panel
        self.plot_panel.add_widget(new_tab)
        new_tab.on_release()

    def remove_tab(self, *args, **kwargs):
        try:
            tabbed_panel = self.plot_panel
            if 'tab' in kwargs:
                tab = kwargs['tab']
            else:
                return
            tabbed_panel.remove_widget(tab)

        except Exception as E:
            print(E, 'failed to remove tab')

        else:
            selected_tab = tabbed_panel.current_tab
            if selected_tab == tab:
                if len(tabbed_panel.tab_list) < 1:
                    self.remove_all_tabs()
                    # tabbed_panel.clear_widgets()
                    # self.root.ids.nav_bar.clear_widgets()
                else:
                    tabbed_panel.switch_to(tabbed_panel.tab_list[-1])
            else:
                return

    def remove_all_tabs(self, *args):
        # nodes = [i for i in self.file_tree.iterate_all_nodes()]
        tabs = [i for i in self.plot_panel.tab_list]
        for tab in tabs:
            self.plot_panel.remove_widget(tab)
        # for node in nodes:
            # self.file_tree.remove_node(node)
        self.plot_panel.clear_widgets()
        self.root.ids.nav_bar.clear_widgets()

    def key_down_action(self, window, keyboard, keycode, text, modifiers):
        if len(modifiers) == 1 and 'ctrl' in modifiers: # commands for control being held down
            if text == 'o':
                dialog = filechooser.FileDialog(self.load_data_file)
                dialog.load_file(configuration.parser['settings']['data_location'])
            else:
                pass
        else:
            pass

    def open_progression(self, attr=None):
        test_tab = self.plot_panel.current_tab

        if test_tab and hasattr(test_tab, "plot_handler"):
            try:
                # test_tab.plot_handler._create_cycle_progression_plot()
                progression = getattr(test_tab.plot_handler, attr)
            except Exception as e:
                print("Failed finding attribute to create plot {}.\n".format(attr))
                print(e)
                return

            canvas = FigureCanvasKivyAgg(progression)
            nav_bar = CustomKivyNavBar(canvas)

            progression_content = BoxLayout(orientation='vertical')
            cycle_slider = ProgressionControl(test_tab.plot_handler, canvas, progression)
            progression_content.add_widget(canvas)
            progression_content.add_widget(cycle_slider)
            progression_content.add_widget(nav_bar.actionbar)

            try:
                setattr(nav_bar.actionbar,'background_image', '')
                setattr(nav_bar.actionbar,'background_color', (.5, .47, .5, 0.7))
            except Exception as e:
                print(e)
                ### attempt to make new window, but doesnt have native support
            # new_window = PopupNewWindow(progression_content)
            # a = multiprocessing.Process(target=new_window.run)
            # a.start()

            popup = Popup(title='Cycle Progression Plot', content=progression_content, size_hint = (.8,.8))
            popup.open()
        else:
            print('test tab has no plot handler')

    def compare_cells(self, cell_two, attr='progression'):
        test_tab = self.plot_panel.current_tab
        test_tab_two = cell_two.actual_parent
        print(type(cell_two))

        if test_tab and hasattr(test_tab, "plot_handler") and  test_tab_two and hasattr(test_tab, "plot_handler"):
            try:
                # test_tab.plot_handler._create_cycle_progression_plot()
                progression_one = getattr(test_tab.plot_handler, attr)
                progression_two = getattr(test_tab_two.plot_handler, attr)
            except Exception as e:
                print("Failed creating cycle progression plot.\n")
                print(e)
                return
            ### create canvas with both plotted
            co_fig = test_tab.plot_handler.create_combined_plot([progression_one, progression_two])

            canvas = FigureCanvasKivyAgg(co_fig)
            nav_bar = CustomKivyNavBar(canvas)

            progression_content = BoxLayout(orientation='vertical')
            #create sliders for control
            cycle_slider_one = ProgressionControl(test_tab.plot_handler, canvas)
            cycle_slider_two = ProgressionControl(test_tab_two.plot_handler, canvas)

            progression_content.add_widget(canvas)
            progression_content.add_widget(cycle_slider_one)
            progression_content.add_widget(cycle_slider_two)
            progression_content.add_widget(nav_bar.actionbar)

            try:
                setattr(nav_bar.actionbar,'background_image', '')
                setattr(nav_bar.actionbar,'background_color', (.5, .47, .5, 0.7))
            except Exception as e:
                print(e)

            popup = Popup(title='dQ/dV Progression Plot', content=progression_content, size_hint = (.8,.8))
            popup.open()
        else:
            print('test tab has no plot handler')

    def analyze_power_data(self, display=True, *args):
        test_tab = self.plot_panel.current_tab
        if test_tab and hasattr(test_tab, "arbin_test"):
            try:
                R_dc, I_peak = test_tab.arbin_test.calculate_power_data()
            except Exception as e:
                print("Failed calculating power test data.\n")
                print(e)
            else:
                #show DCR Data
                stra = "\nCalculated R_dc(ohm): \n"
                for key in R_dc.keys():
                    stra += key+ "  :  "+ str(np.around(R_dc[key], 1)) + "\n"

                #show average current
                strb = "\nCalculated I_peak(A): \n"
                for key in I_peak.keys():
                    strb += key+ "   :  "+ str(np.around(I_peak[key], 4)) + "\n"

                print(stra, strb)
                if display:
                    label = Label(text = stra + strb)
                    test_tab.plot_tab.ids.sidebar.add_widget(label)
                    # pop = Popup(title = "Power Test Results {}".format(test_tab.arbin_test.arbin_ID),
                    #  content = label, size_hint = (None, None))
                    # pop.open()
                else:
                    pass

        else:
            print("no arbin test identified in this tab!")

    # def dict_display(self, dicts):
    #     '''
    #     Designed to visually display calculated power data,
    #     but possible to use for other metrics as well
    #
    #     dicts = dictionary of dictionaries
    #     '''
    #     for item in dicts.keys():
    #         data = dicts[keys] # dictionary containing the data itself
    #         height = len(data.keys()) + 1
    #         width =
    #
    def _on_dropfile(self, window, filepath):
        print("received file drop")
        self.load_data_file(filepath)


def build_app(control_module):
    main_app = DataApp()
    setattr(main_app, 'control_module', control_module)
    main_app.run()

if __name__ == '__main__':
    build_app()
