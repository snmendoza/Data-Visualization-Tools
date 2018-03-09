
###  Test Definitions ###
# contains classes describing arbin tests
# retrieves information from databse, if available
# packs information into classes

### import statements ###
import databases


class ArbinTest(object):

    def __init__(self, excel_file, sheets, ID=None):
        ### data files
        self.source = excel_file # excel file containing primary data
        self.data = self.source.parse(sheets[0]) # data sheet for this test
        self.statistics = self.source.parse(sheets[1])# statistics sheet for this test
        ###

        ### version-specific info
        self.version = sheets[-1] # arbin version
        self.version_keys = self.get_version_keys()
        ###

        ### arbin related info
        self.arbin_ID = ID # this ID
        self.test_info = self.get_arbin_info()
        self.item_ID = str(self.test_info[self.version_keys['Item ID']])
        ###

        ### inferred cell info
        self.electrode_type = self.get_electrode_type()
        ###

        ### cell build info
        try:
            self.cell_build_info = self.get_build_info()
        except Exception as e:
            print(e, '\nfailed to retrieve cell info for {}'.format(self.arbin_ID))
            self.cell_build_info = None
        else:
            print('successfully retreived build info from database : {}'.formate(self.item_ID))
        ###

    def get_version_keys(self):
        '''
        get keys that are version-specific for arbin data files

        '''
        if self.version == 'new':
            return {'Item ID':'Item ID'}
        else:
            return {'Item ID': ' Item_ID'}

    def get_electrode_type(self):
        '''
        Determine electrode type based on Item ID naming convention
        '''
        if 'a' in self.item_ID.lower():
            return 'Anode'
        elif 'c' in self.item_ID.lower():
            return 'Cathode'
        else:
            return 'Full'

    def get_arbin_info(self):
        '''
        Collect information about our test based on the arbin xlsx output
        '''
        ###
        ### get arbin info from gloabl sheet from excel worksheet using item ID

        if self.arbin_ID:
            info_sheet = self.source.parse('Global_Info', skiprows=3).set_index('Channel')
            info = info_sheet.loc[self.arbin_ID]
        else:
            print("Failed to get cell test info from {}".format(self.source))
            info = None
        return info
        ###


    def get_build_info(self):
        '''
        Collect information about our cell/test based on excel sheet with build
        information
        '''
        if databases and hasattr(self,'test_info'):
            if self.electrode_type == 'Anode':
                sheet = databases.test_cell_data.anodes
            elif self.electrode_type     == 'Cathode':
                sheet = databases.test_cell_data.cathodes
            elif self.electrode_type == 'Full':
                sheet = databases.test_cell_data.full_cells
            else:
                pass
        else:
            pass
        name_indexed_sheet = sheet.set_index('Cell Name')
        cell_build_info = name_indexed_sheet.loc[self.item_ID]
        return cell_build_info


    def __iter__(self):
        yield self
