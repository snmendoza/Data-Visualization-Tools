import kivy
kivy.require('1.10.0')
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '1100')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy','exit_on_escape', 0)

from kivy.app import App
from kivy.lang import Builder
from collections import OrderedDict as OrDict
from . menu_definitions import * # custom kivy nav bar
from os.path import basename


import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from kivy.garden.matplotlib.backend_kivy import FigureCanvas


class DataApp(App):

    def build(self, control_module = None):

        self.root = Root()
        self.icon = 'icon.png'

        ### generate important references ##
        # plotting module
        if control_module:
            self.data_plot = control_module
        # file tree
        self.file_tree = self.root.ids.menubar.ids.scrolltree.ids.treeview
        self.plotted_files = []
        #plotting area
        self.plot_panel = self.root.ids.PlotPanel
        return self.root

    def load_data_file(self, file_list):
        '''
        Compatibility check for files that are to be added to the tree view
        file_list should simply be a list of files -  but it is a kivy observable list,
        not an actual list apparently
        '''
        print(file_list)


        try: # catch iteration error
            for file in file_list:
                try: # catching file parsin error
                    self.send_to_tree(file)
                except Exception as e:
                    print('failed to parse {} to file tree'.format(file), e)
        except Exception as e:
            print(e)


    def send_to_tree(self, file):
        '''
        Send input file to opened file tree
        inputs: file path for data (such as arbin .xls)
        outputs: none

        '''
        ### get map of tests and generate arbin tests ###
        if file in self.plotted_files:
            print('File already plotted')
            return
        else:
            self.plotted_files.append(file)
        try:
            test_map = self.control_module.test_mapper.generate_data_mapping(file)
            tests = self.control_module.test_mapper.generate_arbin_tests(test_map)
            tests_as_nodes = [ActiveTreeViewLabel(text = test.item_ID, node_object = test) for test in tests]

        except Exception as e:
            print('failed send to tree \n', e)
        ####

        ### add file as node; add each test as leaf ###
        else:
            node = self.file_tree.add_node(TreeViewLabel(text = basename(file)))
            for subnode in tests_as_nodes:
                self.file_tree.add_node(subnode, node)
            print('successfully added {} to tree'.format(file))
        ####

    def plot_selected(self):
        '''
        Trigger to main app to plot selected files from tree view
        no inputs, no outputs
        '''
        # type references
        plot_handler = self.control_module.PyPlotHandler
        ArbinTest = self.control_module.ArbinTest

        ### get selected node, retrieved as ActiveTreeViewLabel type
        selected_test = self.file_tree.selected_node
        if not selected_test:
            print('no selection made')
            return

        ### get arbin test from node
        arbin_test = selected_test.node_object

        # create plot handler from arbin test
        plot_handler = plot_handler(arbin_test, types=ArbinTest)

        # create canvas and navigation tools, populate layout
        self.generate_plot_tab(plot_handler, arbin_test)

    def generate_plot_tab(self, plot_handler, arbin_test):
        '''
        Takes in figure and generates a plot tab, adds tab to the plot panel
        '''
        ### send signal to generate plots
        plot_handler.create_plots()
        ### create custom plot tab
        new_tab = PlotPanelItem(plot_handler, arbin_test,root=self.root, text=arbin_test.item_ID)
        ### add tab to tabbed panel
        self.plot_panel.add_widget(new_tab)
        new_tab.on_release()


def build_app(control_module):
    main_app = DataApp()
    setattr(main_app, 'control_module', control_module)
    main_app.run()

if __name__ == '__main__':
    build_app()
