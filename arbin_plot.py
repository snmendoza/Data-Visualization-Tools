# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 13:49:57 2018

@author: Sean
"""

import pandas as pd
import file_utils
import xlrd
from matplotlib import pyplot as plt
from collections import OrderedDict as OrDict
import numpy as np
from plot_handlers import BokehPlotHandler, PyPlotHandler


class TestMapper(object):

    
    def __init__(self):
        self.lut = {'new': {'channel':'Channel_{}_1',
                            'statistics': 'StatisticsByCycle-Chan_{}'},
                    'old': {'channel':'Channel_{}',
                            'statistics': 'Statistics_{}'}}
        self.version = 'old'
        
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
            
            ## determine naming convention by version
            if '7.00' in self.info['Software Version'].iloc[1]:
                self.version = 'new'
                self.convention = self.lut['new']
            else:
                self.version = 'old'
                self.convention = self.lut['old']
                
                
            channels = self.info['Channel'][:]
            
            mapping = {}
            ### store map into dictionary

            for channel_name in channels:
                statistics = self.convention['statistics'].format(channel_name)
                data = self.convention['channel'].format(channel_name)
                
                mapping[channel_name] = (data, statistics, self.version)
                
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
        self.version = sheets[-1]
        
        if ID:
            self.ID = ID
            info_sheet = self.source.parse('Global_Info', skiprows=3).set_index('Channel')
            self.info = info_sheet.loc[self.ID]
        else:
            pass
        
    def __iter__(self):
        yield self
           

def startup():
    '''
    Get source file for tests, 
    Parse out what tests exist in the file using test mapper
    return arbin test mapping
    '''
    source = file_utils.get_file()
    data_reader = TestMapper()
    mapping = data_reader.generate_data_mapping(source)
    arbin_tests = data_reader.generate_arbin_tests(mapping)
    return arbin_tests

def plotting(arbin_tests):
    test_dict = {}
    if type(arbin_tests) is list:
        for test in arbin_tests:
            test_dict[test] = PyPlotHandler(test, types=ArbinTest)
            test_dict[test].create_plots()
            test_dict[test].show()
    else:
        plotter = PyPlotHandler(arbin_tests, types=ArbinTest)
        plotter.create_plots()
        plotter.show()
        
if __name__ == "__main__":
    arbin_tests = startup()
    plotting(arbin_tests)