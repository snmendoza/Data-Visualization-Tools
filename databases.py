

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
        self.filepath = filepath
        self.excel_file = self.reload_database(filepath = self.filepath)

    def reload_database(self, filepath = None):
        if not filepath:
            filepath = self.filepath
        else:
            pass

        try:
            excel_file = pd.ExcelFile(filepath)
        except Exception as e:
            print('Failed to Load Excel DB:', e)

        try:
            self.anodes = excel_file.parse('Anode Cell', skiprows=1)
        except Exception as e:
            print('Failed to DB Anode Sheet:', e)

        try:
            self.cathodes = excel_file.parse('Cathode Cell', skiprows=1)
        except Exception as e:
            print('Failed to Load DB Cathode Sheet', e)

        try:
            self.full_cells = excel_file.parse('Full Cell')
        except Exception as e:
            print('Failed to Load DB Full-Cell sheet:', e)

        return excel_file




parser = configuration.parser
test_cell_data_path = parser.get('databases', 'test_cell_data')
test_cell_data = TestCellData(test_cell_data_path)
