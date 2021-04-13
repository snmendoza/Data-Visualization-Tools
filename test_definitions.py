
###  Test Definitions ###
# contains classes describing arbin tests
# retrieves information from databse, if available
# packs information into classes

### import statements ###
import databases
import numpy as np
from os import path

class ArbinTest(object):

    def __init__(self, excel_file, sheets, ID=None):
        ### data files
        self.source = excel_file # excel file containing primary data
        self.filename = path.split(self.source.io)[1]
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
        try:
            self.item_ID = str(self.test_info[self.version_keys['Item ID']])
        except:
            print("No item ID found (deprecated in newer MITSPro)")
            self.item_ID = 0
        ###

        ### inferred cell info
        self.electrode_type = self.get_electrode_type()
        self.electrode_active_mass = 1
        ###

        ### cell build info
        try:
            self.cell_build_info = self.get_build_info()
        except Exception as e:
            print(e, '\nDid not retrieve cell info for {} as database is no longer in use'.format(self.arbin_ID))
            self.cell_build_info = None
        else:
            print('successfully retreived build info from database : {}'.format(self.item_ID))
        ###

    def get_version_keys(self):
        '''
        get keys that are version-specific for arbin data files

        '''
        if self.version == 'new' or self.version == 'mits8':
            return {'Item ID':'Item ID'}
        else:
            return {'Item ID': ' Item_ID'}

    def get_electrode_type(self):
        '''
        Determine electrode type based on Item ID naming convention
        '''
        if 'a-' in self.filename.lower():
            return 'Anode'
        elif 'c-' in self.filename.lower():
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
        name_indexed_sheet = sheet.set_index('Cell  Name')
        cell_build_info = name_indexed_sheet.loc[self.item_ID]
        return cell_build_info

    def calculate_power_data(self, *args):
        schedule_string = self.test_info['Schedule File Name'].lower()
        if 'power' in schedule_string:
            print('power test schedule recognized')
        else:
            print('power test schedule not recognized')
            #POPUP
            return

        if 'cathode' in schedule_string:
            DCR_SOC0 = 12
            DCR_SOC50a = 18
            DCR_SOC50b = 22
            DCR_SOC100 = 28

            PWR_SOC0 = 14
            PWR_SOC50a =20
            PWR_SOC50b = 24
            PWR_SOC100 = 30

        elif 'anode' in schedule_string:
            DCR_SOC0 = 11
            DCR_SOC50a = 17
            DCR_SOC50b = 21
            DCR_SOC100 = 27

            PWR_SOC0 = 13
            PWR_SOC50a = 19
            PWR_SOC50b = 23
            PWR_SOC100 = 29

        elif 'full' in schedule_string:
            print('full cell criteria not yet determined')
            return
        else:
            return

        steps_data = self.data.set_index('Step_Index')

        ### Calculate DCR ###
        ### DCR = (V2 - V1) / Ip

        DCR = {'SOC 0+1C': self.calculate_DCR(steps_data, DCR_SOC0)
                ,'SOC 50+1C': self.calculate_DCR(steps_data, DCR_SOC50a)
                ,'SOC 50-1C': self.calculate_DCR(steps_data, DCR_SOC50b)
                ,'SOC 100-1C': self.calculate_DCR(steps_data, DCR_SOC100)}

        ###

        ###
        I = {'SOC 0+': self.calculate_I(steps_data, PWR_SOC0)
                ,'SOC 50+': self.calculate_I(steps_data, PWR_SOC50a)
                ,'SOC 50-': self.calculate_I(steps_data, PWR_SOC50b)
                ,'SOC 100-': self.calculate_I(steps_data, PWR_SOC100)}

        ###
        ###

        return DCR, I
        # Low SOC, DCR+, PWR+
        # Mid SOC, DCR+, DCR-, PWR+, PWR-
        # High SOC, DCR-, PWR+

    def calculate_DCR(self, data, pulse_index):
        '''
        data = full dataframe of test, must be indexed by step index
        pulse_index = must be step index of pulse current

        '''
        try:
            print(data.loc[pulse_index]['Voltage(V)'], pulse_index)
            vb = data.loc[pulse_index]['Voltage(V)'].iloc[-2] # use second to last data point
            va = data.loc[pulse_index - 1]['Voltage(V)'].iloc[-1]
            i = data.loc[pulse_index]['Current(A)'].iloc[-2]

            dcr = (vb - va) / i
        except Exception as e:
            print(e)
            dcr = np.nan
        return dcr

    def calculate_I(self, data, pulse_index):
        '''
            calcules the average CURRENT during a given pulse. Power draw/
            delivery depends on voltage.
        data = full dataframe of test, must be indexed by step index
        pulse_index = must be step index of voltage_hold or pulse in question
        returns the average current over that pulse by calculating total capacity delivered
        and averaging over pulse length

        '''
        try:
            i_mean = np.mean(data.loc[pulse_index]['Current(A)']) # essentially finds current polarity

            if i_mean < 0:
                Qb = data.loc[pulse_index]['Discharge_Capacity(Ah)'].iloc[-1]
                Qa = data.loc[pulse_index - 1]['Discharge_Capacity(Ah)'].iloc[-1]

            elif i_mean > 0:
                Qb = data.loc[pulse_index]['Charge_Capacity(Ah)'].iloc[-1]
                Qa = data.loc[pulse_index - 1]['Charge_Capacity(Ah)'].iloc[-1]

            else:
                print('PWR current polarity not determined')
                return 'ERR'

            dQ = Qb - Qa
            time_s = max(data.loc[pulse_index]['Test_Time(s)']) - min(data.loc[pulse_index]['Test_Time(s)'])
            time_h = time_s / 3600
            PWR_current = dQ  / time_h
        except Exception as e:
            print(e)
            PWR_current = np.nan

        return PWR_current



    def __iter__(self):
        yield self
