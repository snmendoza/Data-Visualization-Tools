# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 13:49:57 2018

@author: Sean
"""

import pandas as pd
from file_utils import *
import xlrd
from matplotlib import pyplot as plt
from collections import OrderedDict as OrDict
import numpy as np

burgundy = (0.553,0.059,0.071)
dark_green = (0.039,0.369,0.267)
dark_orange = (0.922,0.345,0.008)
dark_blue = (0.1, .0, .6)



#####  Color Palette by Paletton.com
#####  Palette URL: http://paletton.com/#uid=3380l0krHlZrzwItlsssEhQu6bm


#*** Green shades:
#
#   shade 0 = #107455 = rgb( 16,116, 85) = rgba( 16,116, 85,1) = rgb0(0.063,0.455,0.333)
#   shade 1 = #18AA7E = rgb( 24,170,126) = rgba( 24,170,126,1) = rgb0(0.094,0.667,0.494)
#   shade 2 = #0C966C = rgb( 12,150,108) = rgba( 12,150,108,1) = rgb0(0.047,0.588,0.424)
#   shade 3 = #0A5E44 = rgb( 10, 94, 68) = rgba( 10, 94, 68,1) = rgb0(0.039,0.369,0.267)
#   shade 4 = #043C2B = rgb(  4, 60, 43) = rgba(  4, 60, 43,1) = rgb0(0.016,0.235,0.169)
#
#*** Orange Shades (1):
#
#   shade 0 = #AF6A18 = rgb(175,106, 24) = rgba(175,106, 24,1) = rgb0(0.686,0.416,0.094)
#   shade 1 = #FF9B23 = rgb(255,155, 35) = rgba(255,155, 35,1) = rgb0(1,0.608,0.137)
#   shade 2 = #E38413 = rgb(227,132, 19) = rgba(227,132, 19,1) = rgb0(0.89,0.518,0.075)
#   shade 3 = #8E540F = rgb(142, 84, 15) = rgba(142, 84, 15,1) = rgb0(0.557,0.329,0.059)
#   shade 4 = #5A3405 = rgb( 90, 52,  5) = rgba( 90, 52,  5,1) = rgb0(0.353,0.204,0.02)
#
#*** Burgundy Shades (2):
#
#   shade 0 = #AE171B = rgb(174, 23, 27) = rgba(174, 23, 27,1) = rgb0(0.682,0.09,0.106)
#   shade 1 = #FD2329 = rgb(253, 35, 41) = rgba(253, 35, 41,1) = rgb0(0.992,0.137,0.161)
#   shade 2 = #E11318 = rgb(225, 19, 24) = rgba(225, 19, 24,1) = rgb0(0.882,0.075,0.094)
#   shade 3 = #8D0F12 = rgb(141, 15, 18) = rgba(141, 15, 18,1) = rgb0(0.553,0.059,0.071)
#   shade 4 = #5A0507 = rgb( 90,  5,  7) = rgba( 90,  5,  7,1) = rgb0(0.353,0.02,0.027)
#

#####  Generated by Paletton.com (c) 2002-2014


class TestMapper(object):

    def generate_data_mapping(self, source):
        """
        Sets a source ".xlsx" file for TestMapper to read from.
        Opens dataframe 
        
        Inputs: arbin xlsx data file
        Outputs: mapping of test IDs and their sheet names
        
        """
        if ".xls" not in source:
            print("Expecting xls or xlsx, got {} instead".format(str(source)[-4:]))
            pass
        else:
            ### store the source file
            self.excel_file = pd.ExcelFile(source)
            
            ### get info on names of other tabs to pair and search for
            self.info = self.excel_file.parse('Global_Info', skiprows=3)
            channels = self.info['Channel'][:]
            
            mapping = {}
            ### store map into dictionary
            for channel_name in channels:
                statistics = "Statistics_" + str(channel_name)
                data = "Channel_" + str(channel_name)
                
                mapping[channel_name] = (data, statistics)
                
        self.mapping = mapping
        return mapping
                
    def generate_arbin_tests(self, mapping):
        """
        Takes sheet info and turns into arbin test objects
        
        Input: mapping dictionary {test ID: (data sheet name, stat sheetname)}...
        Output: single arbin test or list of arbin test objects
        
        """
        keys = mapping.keys()
        if len(keys) == 0: # no tests 
            self.tests = None
            pass
        
        elif len(keys) == 1: # single test; return single test
            test = ArbinTest(self.excel_file, mapping[keys[0]], ID=keys[0])
            self.tests = [test]
            return test
        
        else: # multiple tests, return list of tests
            tests = []
            for key in keys:
                test_object = ArbinTest(self.excel_file, mapping[key], key)
                tests.append(test_object)
            self.tests = tests
            return tests
            
class ArbinTest(object):
    
    def __init__(self, excel_file, sheets, ID=None):
        self.source = excel_file
        self.data = self.source.parse(sheets[0])
        self.statistics = self.source.parse(sheets[1])
        
        if ID:
            self.ID = ID
            info_sheet = self.source.parse('Global_Info', skiprows=3).set_index('Channel')
            self.info = info_sheet.loc[self.ID]
        else:
            pass
    def __iter__(self):
        yield self
            
        
class PlotHandler(object):
    
    def __init__(self, tests=[]):
        if type(tests) in [list, ArbinTest]:
            self.tests = list(tests)
        else:
            print('invalid tests')
            pass
        
        self.gs_data = plt.GridSpec(7, 8, hspace=0.001) # split into 5 rows and 1 column, space for title and table

        self.figure = plt.figure(figsize=(8,8))
        # voltage/current curves
        self.ax1 = self.figure.add_subplot(self.gs_data[2:4,:])#, colspan=4, rowspan=2)
        # capacity data
        self.ax2 = self.figure.add_subplot(self.gs_data[0:2,:], sharex=self.ax1)#, colspan=4, rowspan=2, sharex=self.ax1)
        # step index area
        self.ax4 = self.figure.add_subplot(self.gs_data[4,:], sharex=self.ax1)#, colspan=4, rowspan=1, sharex=self.ax1)
        # samples info area
        self.ax3 = self.figure.add_subplot(self.gs_data[6, 2:])#plt.subplot2grid((8,4), (6,1), colspan=3, rowspan=4)

        

    def add_test(self, arbin_test):
        if type(arbin_test) == ArbinTest and arbin_test not in self.tests:
            self.tests.append(arbin_test)
        elif arbin_test in self.tests:
            print('test aready in tests')
            pass
    
    def create_plots(self):
        if not self.tests:
            print('no tests added. add test.')
            pass
        else:
            self._create_CV_plot()
            self._create_stepQ_plot()
            self._create_infotable()
            self._create_stepix_plot()
            self._create_title()
    
    def _create_title(self):
        title = 'Cell '
        for test in self.tests:
            title += '{} ({})\n'.format(test.info['Chan_Num'], test.ID)
        self.title = title
    
    def _create_CV_plot(self):
        v_plot = self.ax1 # get a reference to the axes object
        v_plot.set_ylabel('Voltage', color=dark_orange)
        v_plot.tick_params('y', colors=dark_orange)
        v_plot.get_yaxis().set_label_coords(-0.05,0.5)
        plt.setp(v_plot.get_xticklabels(), visible=False)
        # set up the second axis
        i_plot = v_plot.twinx()
        i_plot.set_ylabel('Current(mA)', color = dark_blue)
        i_plot.tick_params('y', colors=dark_blue)
        
        # set up the first axis
#        v_plot.set_xlabel('Test Time(s)')
        v_plot.set_ylabel('Voltage')#, color=burgundy)
#        stepq_plot.tick_params('y', colors=burgundy)
        
        
        for test in self.tests:
            # retrieve the data
            i = test.data['Current(A)'] * 1000
            v = test.data['Voltage(V)']
            t = test.data['Test_Time(s)']
            #Plot the data
            v_plot.plot(t, v, color=dark_orange, linewidth=0.6)
            i_plot.plot(t, i, color=dark_blue, linewidth=0.6)
        
            
    def _create_stepQ_plot(self):
        stepq_plot = self.ax2 # get a reference to the axes object
        plt.setp(stepq_plot.get_xticklabels(), visible=False)
        stepq_plot.set_ylabel('Capacity (mAh)')
        stepq_plot.get_yaxis().set_label_coords(-0.05,0.5)
        
        for test in self.tests:
            # retrieve the data
            qc = test.statistics['Charge_Capacity(Ah)'] * 1000
            qd = test.statistics['Discharge_Capacity(Ah)'] * 1000
            t = test.statistics['Test_Time(s)']
            #Plot the data
            stepq_plot.scatter(t, qc, color=burgundy, s=2.5, label=None)
            stepq_plot.scatter(t, qd, color=dark_green, s=2.5, label=None)
            stepq_plot.plot(t, qc, color=burgundy, linewidth=0.9, label='Charge')
            stepq_plot.plot(t, qd, color=dark_green, linewidth=0.9, label='Discharge')
        
        stepq_plot.legend(loc='best')
        stepq_plot.set_ylim(bottom=0)
        stepq_plot.set_xlim(left=0)
    
    def _create_infotable(self):
        infotable = self.ax3
        infotable.axis('tight')
        infotable.axis('off')
        
        global_info = self.tests[0].source.parse('Global_Info', skiprows=3).set_index('Channel')
        rows = global_info.keys()
        
        data = OrDict()
        ids = []
        # create data dictionary for each row name
        for row in rows:
            data[row] = []
            for test in self.tests:
                datum = global_info.loc[test.ID][row]
                data[row].append(datum)
                ids.append(test.ID)
            
        # delete entries that do not contain info
        
        for row in rows:  # for each row name
            values = data[row] # these are the values
            valid = any(bool(value) and value == value for value in values) # if any value is bool true
            if valid: # proceed as normal
                pass
            else: # delete the pair
                del data[row]
        try:
            del data['Schedule_File_Name']
        except:
            pass
        
#        ids = []
#        for tests in self.tests:
#            column = [x for x in global_info.loc[test.ID] if x and x==x]
#            data.append(column)
#            ids.append(test.ID)
        table_data = [data[row] for row in rows if row in data.keys()]
#        data = np.transpose(np.array(data))
        
        table = infotable.table(cellText=table_data, rowLabels=list(data.keys()), colLabels=ids, loc=0)
        
    def _create_stepix_plot(self):
        cycle = self.ax4 # get a reference to the axes object
#        cycle.yaxis.set_visible(False)
        cycle.set_yticklabels([])
        cycle.yaxis.set_tick_params(size=0)
#        cycle.spines['right'].set_visible(False)
#        cycle.spines['left'].set_visible(False)
#        cycle.spines['top'].set_visible(False) 
#        cycle.xaxis.set_visible(False)
        
        cycle.set_ylabel('Cycle Index')
        cycle.set_xlabel('Test Time(s)')
        cycle.set_ylim(bottom=0.9, top=1.1)
        cycle.get_yaxis().set_label_coords(-0.05,0.5)
        for test in self.tests:
            # retrieve the data
            cyc = test.statistics["Cycle_Index"]
            t = test.statistics['Test_Time(s)']
            y = [1] * len(t)
            
            #Plot the data

            t5 = [time for c, time in zip(cyc, t) if not c % 5]
            t_not5 = [time for c, time in zip(cyc, t) if c % 5]
            y5 = [1] * len(t5)
            y_not5 =[1] * len(t_not5)
            
            cycle.scatter(t5, y5, color=(0.85,0,0), marker='|')
            cycle.scatter(t_not5, y_not5, color=(0,0,0.8), marker='|')
            
            for index, values in enumerate(zip(t, y)):
                x, y = values
                y = y + 0.05
                values = (x,y)
                N = cyc.iloc[index]
                if not bool(int(N) % 5):
                    time = values[0]
                    cycle.annotate(N, xy=values, textcoords='data')
                else:
                    pass
            
    def show(self):
        self.figure.subplots_adjust(hspace=0.001)
        self.figure.suptitle(self.title)
        self.figure.tight_layout()
        self.figure.show()
        
        
    
    
if __name__ == "__main__":
#     select data file
#    source = get_file()
    # create a parser for it
#    data_reader = TestMapper()
    # map it to tests
#    mapping = data_reader.generate_data_mapping(source)
    # convert mapping to tests
    arbin_tests = data_reader.generate_arbin_tests(mapping)
    # create a plotter
#    for test in arbin_tests:
    plotter = PlotHandler(arbin_tests[2])
    # generate the plots itnernally
    plotter.create_plots()
    # show
    plotter.show()