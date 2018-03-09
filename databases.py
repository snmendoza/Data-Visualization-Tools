

import configuration
import pandas as pd
'''
Module containing test cell database, based on the path specified in the config file
access cell build info for cathode, anode, or full cells line_width

import databases
databases.test_cell_data.anodes
databases.test_cell_data.cathodes
databases.test_cell_data.full_cells

etc.

'''

class TestCellData(object):
    def __init__(self, filepath):
        excel_file = pd.ExcelFile(filepath)
        self.anodes = excel_file.parse('Anode Cell', skiprows=1)
        self.cathodes = excel_file.parse('Cathode Cell', skiprows=1)
        self.full_cells = excel_file.parse('Full Cell')


parser = configuration.parser
test_cell_data_path = parser.get('databases', 'test_cell_data')
test_cell_data = TestCellData(test_cell_data_path)
