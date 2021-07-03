# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 14:21:23 2018

@author: Sean
"""

# pyplot imports
import matplotlib
# matplotlib.use('module://kivy.garden.matplotlib.backend_kivyagg')

from matplotlib import pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.figure import Figure
import configuration
from collections import OrderedDict as OrDict
import numpy as np
from scipy.signal import medfilt, savgol_filter
from copy import copy
np.errstate(divide='ignore')

burgundy = (0.553,0.059,0.071)
dark_green = (0.039,0.369,0.267)
dark_orange = (0.922,0.345,0.008)
dark_blue = (0.1, .0, .6)

black = (0.05,0.05,0.5)
stark_red = (0.5, .05, .05)
grey = (0.5, 0.5, 0.5)


Seq2Colormap = ['autumn',  'winter','summer','spring', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
             'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']

class PlotHandler(object):
    def __init__(self, tests, types):
        self.tests = list(tests)

        self.omit = ['Schedule Version', 'Software Version', 'Has Aux', 'Has Specail',
             'Log Aux Data Flag','Log Special Flag' , 'Serial Number', 'Volt',
             'ChanStat']

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
            # self._create_infotable()
            self._create_stepix_plot()
            self._create_title()
            self._create_cycle_progression_plot()
            self._create_dqdv_progression_plot()

            self.figure.subplots_adjust(hspace=0.001)
            self.figure.suptitle(self.title)


class CyclesHandler(Figure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cycle_data = None
        self.charge_lines = OrDict()
        self.discharge_lines = OrDict()


class PyPlotHandler(PlotHandler):

    def __init__(self, tests=[], types=None):
        super().__init__(tests, types)

        self.cycles_handler = CyclesHandler()
        self.charts = [] # contains i, v, q, and ce chart refs
        self.gs_data = plt.GridSpec(20, 8, hspace=0.001) # split into 20 rows and 1 column, space for title and table

        self.figure = plt.figure(figsize=(8,8))
        # voltage/current curves
        self.ax1 = self.figure.add_subplot(self.gs_data[7:18,:])#, colspan=4, rowspan=2)
        # capacity data
        self.ax2 = self.figure.add_subplot(self.gs_data[0:7,:], sharex=self.ax1)#, colspan=4, rowspan=2, sharex=self.ax1)
        # step index area
        self.ax4 = self.figure.add_subplot(self.gs_data[18:20,:], sharex=self.ax1)#, colspan=4, rowspan=1, sharex=self.ax1)
        # samples info area
        # self.ax3 = self.figure.add_subplot(self.gs_data[6, 2:])#plt.subplot2grid((8,4), (6,1), colspan=3, rowspan=4)

        self.progression = plt.figure(FigureClass=CyclesHandler)
        self.ax5 = self.progression.add_subplot(111)
        # self.progression.subplots_adjust(bottom=0.25)

        self.dqdv = plt.figure(FigureClass=CyclesHandler)
        self.ax6 = self.dqdv.add_subplot(111)

        ## table data to ignore
        self.omit = ['Schedule Version', 'Software Version', 'Has Aux', 'Has Specail',
                     'Log Aux Data Flag','Log Special Flag' , 'Serial Number', 'Volt',
                     'ChanStat']
#
    def _create_title(self):
        title = ''
        title_format = ' {} Cell {} (ch {})'
        for test in self.tests:
            # electrode = test.electrode_type
            # item_id = test.item_ID
            # chan = test.arbin_ID

            entry = test.title
            title += entry + ';'

        subtitle = '\nfile: {}'.format(self.tests[0].source.io)

        self.title = title + subtitle

    def _create_CV_plot(self):
        v_plot = self.ax1 # get a reference to the axes object
        self.charts.append(v_plot)
        v_plot.set_ylabel('Voltage', color=dark_blue)
        v_plot.tick_params('y', colors=dark_blue)
        v_plot.get_yaxis().set_label_coords(-0.07,0.5)
        plt.setp(v_plot.get_xticklabels(), visible=False)
        # set up the second axis
        i_plot = v_plot.twinx()
        self.charts.append(i_plot)
        i_plot.set_ylabel('Current(mA)', color = burgundy)
        i_plot.tick_params('y', colors=burgundy)

        # set up the first axis
#        v_plot.set_xlabel('Test Time(s)')
        v_plot.set_ylabel('Voltage')#, color=burgundy)
#        stepq_plot.tick_params('y', colors=burgundy)


        for test in self.tests:
            # retrieve the data
            i = test.data['Current(A)'] * 1000
            v = test.data['Voltage(V)']
            t = test.data['Test_Time(s)'] / 3600
            if test.cell_type == "AuxVCell":
                v_anode = test.data["Voltage_Anode(V)"]
                v_cathode = test.data["Voltage_Cathode(V)"]

                v_plot.anode_line  = v_plot.plot(t, v_anode, color="green", linewidth=0.6, alpha=1.0)
                v_plot.cathode_line = v_plot.plot(t, v_cathode, color="red", linewidth=0.6, alpha=1.0)
            #Plot the data
            v_plot.plot(t, v, color=black, linewidth=0.6)
            i_plot.plot(t, i, color=stark_red, linewidth=0.6)


    def _create_stepQ_plot(self):
        '''
        To redraw with mass:
        '''
        stepq_plot = self.ax2 # get a reference to the axes object
        self.charts.append(stepq_plot)

        ### capacity plot
        plt.setp(stepq_plot.get_xticklabels(), visible=False)
        stepq_plot.set_ylabel('Capacity (mAh)')
        stepq_plot.get_yaxis().set_label_coords(-0.07,0.5)

        ### coulombic efficiency plot
        step_CE_plot = stepq_plot.twinx()
        self.charts.append(step_CE_plot)
        step_CE_plot.set_ylabel('Coulombic Efficiency', color = grey)
        step_CE_plot.set_ylim(.95, 1.05)


        for test in self.tests:
            # retrieve the data
            qc = test.statistics['Charge_Capacity(Ah)'] * 1000
            qd = test.statistics['Discharge_Capacity(Ah)'] * 1000

            #calculate coulombic efficiency
            if test.electrode_type == 'Anode': # coulombic efficiency is defined in reverse for anode
                ce = [c / d if d else 0 for c, d in zip(qd, qc)]
            else:
                ce = [d / c if c else 0 for d, c in zip(qd, qc)]

            t = test.statistics['Test_Time(s)'] / 3600

            # get active material weight
            mass_header = configuration.parser['settings']['mass_header']
            if test.cell_build_info is not None and str(test.cell_build_info[mass_header]) != '':
                mass = float(test.cell_build_info[mass_header]) / 1000
                qc = qc / mass
                qd = qd / mass
                stepq_plot.set_ylabel('Capacity (mAh/g)')
            else:
                pass

            #Plot the data
            test.qc_plot, = stepq_plot.plot(t, qc, marker='o', ls='', color=dark_orange, label='Charge Capacity')
            test.qd_plot, = stepq_plot.plot(t, qd, marker='o', ls='', color=dark_blue, label='Discharge Capacity')
            test.ce_plot, = step_CE_plot.plot(t, ce, marker='o',ls='', markersize=1.5, markerfacecolor='none', markeredgecolor=grey)
            # test.ce_plot.set_ylim(0.95, 1.05)
        stepq_plot.legend(loc='best')
        stepq_plot.set_ylim(bottom=0)
        stepq_plot.set_xlim(left=0)
        # return self.ax2

    def _create_infotable(self):
        '''
        Creates table of information
        '''
        infotable = self.ax3 # axis ref
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
                datum = global_info.loc[test.arbin_ID][row]
                data[row].append(datum)
                ids.append(test.arbin_ID)

        # delete entries that do not contain info

        for row in rows:  # for each row name
            values = data[row] # these are the values
            valid = any(bool(value) and value == value for value in values) # if any value is bool true
            if valid and row not in self.omit: # proceed as normal
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
        cycle.set_xlabel('Test Time(hrs)')
        cycle.set_ylim(bottom=0.9, top=1.1)
        cycle.get_yaxis().set_label_coords(-0.07,0.5)
        for test in self.tests:
            # retrieve the data
            cyc = test.statistics["Cycle_Index"]
            t = test.statistics['Test_Time(s)'] / 3600
            y = [1] * len(t)

            #Plot the data
            # get every 5th data point and not 5th data point separately
            t5 = [time for c, time in zip(cyc, t) if not c % 5]
            t_not5 = [time for c, time in zip(cyc, t) if c % 5]

            y5 = [1] * len(t5)
            y_not5 =[1] * len(t_not5)

            cycle.plot(t5, y5, color=(0.85,0,0), marker='|', ls='')
            cycle.plot(t_not5, y_not5, color=(0,0,0.8), marker='|', ls='')

            for index, values in enumerate(zip(t, y)):
                x, y = values
                y = y + 0.05
                values = (x,y)
                N = cyc.iloc[index]
                if not bool(int(N) % 5):
                    cycle.annotate(N, xy=values, textcoords='data')
                else:
                    pass

    def _create_cycle_progression_plot(self):
        """

        """
        self.ax5.set_ylabel('Voltage')
        self.ax5.set_xlabel('Capacity(mAh)')

        for test in self.tests:
            data = test.data
            max_cycle = max(data["Cycle_Index"])
            self.cycle_max = max_cycle
            cycles_data = data.set_index("Cycle_Index")
            self.cycles_handler.cycles_data = cycles_data

            norm = matplotlib.colors.Normalize(vmin=1, vmax=max_cycle)
            cmap = matplotlib.cm.ScalarMappable(norm=norm, cmap=matplotlib.cm.jet)
            cmap.set_array([])

            colorbar = self.progression.colorbar(cmap)
            colorbar.set_label('Cycle')
            for cycle in range(max_cycle):
                charge_lines=[]
                discharge_lines=[]
                cycle_data = cycles_data.loc[cycle + 1]

                #find index of transition from charge to discharge (or vice versa, whichever is first)
                try:
                    charge_end = cycle_data['Charge_Capacity(Ah)'].values.argmax()
                    discharge_end = cycle_data['Discharge_Capacity(Ah)'].values.argmax()
                    cycle_transition = min(discharge_end, charge_end) # i guess this will also plot the rest time but thats okay for now
                #slice data into first and second halves
                except Exception as e:
                    print('omitting cycle error calculating voltages:', e)
                    charge_lines = self.ax5.plot([0],[0], color=cmap.to_rgba(cycle), linewidth=0.6)
                    discharge_lines = self.ax5.plot([0],[0], color=cmap.to_rgba(cycle), linewidth=0.6)
                    charge_capacity = [np.nan]
                    discharge_capacity = [np.nan]
                else:
                    if charge_end < discharge_end:
                        charge = cycle_data.iloc[:cycle_transition]
                        discharge = cycle_data.iloc[cycle_transition:]

                    elif discharge_end < charge_end:
                        charge = cycle_data.iloc[cycle_transition:]
                        discharge = cycle_data.iloc[:cycle_transition]

                    else:
                        print('unable to determine charge order') # if cannot determine, make a random guess
                        charge = cycle_data.iloc[cycle_transition:]
                        discharge = cycle_data.iloc[:cycle_transition]
                    print(len(charge), len(discharge))
                    # plot data on same plot
                    charge_capacity = charge["Charge_Capacity(Ah)"]*1000
                    charge_voltage = charge["Voltage(V)"]

                    discharge_capacity = discharge["Discharge_Capacity(Ah)"]*1000
                    discharge_voltage = discharge["Voltage(V)"]
                    ###### If auxilary
                    if test.cell_type == "AuxVCell":
                        charge_anode_voltage = charge["Voltage_Anode(V)"]
                        charge_cathode_voltage = charge["Voltage_Cathode(V)"]

                        discharge_anode_voltage = discharge["Voltage_Anode(V)"]
                        discharge_cathode_voltage = discharge["Voltage_Cathode(V)"]
                        ## Charge/Discharge: Anode/Cathode/FULL: Voltage; CCV, CAV, etc.
                        CAV, = self.ax5.plot(charge_capacity, charge_anode_voltage, "-.", color=cmap.to_rgba(cycle), linewidth=0.6)
                        CCV, = self.ax5.plot(charge_capacity, charge_cathode_voltage, "--", color=cmap.to_rgba(cycle), linewidth=0.6)

                        DAV, = self.ax5.plot(discharge_capacity, discharge_anode_voltage, "-.", color=cmap.to_rgba(cycle), linewidth=0.6)
                        DCV, = self.ax5.plot(discharge_capacity, discharge_cathode_voltage, "--", color=cmap.to_rgba(cycle), linewidth=0.6)

                        charge_lines.extend([CAV, CCV])
                        discharge_lines.extend([DAV, DCV])

                    else:
                        pass

                    CFV, = self.ax5.plot(charge_capacity, charge_voltage, color=cmap.to_rgba(cycle), linewidth=0.6)
                    DFV, = self.ax5.plot(discharge_capacity, discharge_voltage, color=cmap.to_rgba(cycle), linewidth=0.6)

                    charge_lines.append(CFV)
                    discharge_lines.append(DFV)
                    print(charge_lines)
                    # add pointer to specific lines for later use
                self.progression.charge_lines[cycle + 1] = (charge_lines, charge_capacity)
                self.progression.discharge_lines[cycle + 1] = (discharge_lines, discharge_capacity)

    def _create_dqdv_progression_plot(self):
        """

        """
        self.ax6.set_ylabel('dQ/dV')
        self.ax6.set_xlabel('Voltage')

        for test in self.tests:
            data = test.data
            max_cycle = max(data["Cycle_Index"])
            cycles_data = data.set_index("Cycle_Index")

            norm = matplotlib.colors.Normalize(vmin=1, vmax=max_cycle)
            cmap = matplotlib.cm.ScalarMappable(norm=norm, cmap=matplotlib.cm.jet)
            cmap.set_array([])

            colorbar = self.dqdv.colorbar(cmap)
            colorbar.set_label('Cycle')
            for cycle in range(max_cycle):
                charge_lines=[]
                discharge_lines=[]
                cycle_data = cycles_data.loc[cycle + 1]
                #find index of transition from charge to discharge (or vice versa, whichever is first)
                try:
                    charge_end = cycle_data['Charge_Capacity(Ah)'].values.argmax()
                    discharge_end = cycle_data['Discharge_Capacity(Ah)'].values.argmax()
                    cycle_transition = min(discharge_end, charge_end) # i guess this will also plot the rest time but thats okay for now
                #slice data into first and second halves
                except Exception as e:
                    print('omitting cycle error calculating voltages:', e)
                    discharge_lines = self.ax6.plot([0][0], color=cmap.to_rgba(cycle), linewidth=0.6)
                    charge_lines = self.ax6.plot([0],[0], color=cmap.to_rgba(cycle), linewidth=0.6)
                    vfd = [np.nan]
                    vfc = [np.nan]
                else:
                    if charge_end < discharge_end:
                        charge = cycle_data.iloc[:cycle_transition]
                        discharge = cycle_data.iloc[cycle_transition:]

                    elif discharge_end < charge_end:
                        charge = cycle_data.iloc[cycle_transition:]
                        discharge = cycle_data.iloc[:cycle_transition]

                    else:
                        print('unable to determine charge order')
                        charge = cycle_data.iloc[cycle_transition:]
                        discharge = cycle_data.iloc[:cycle_transition]

                    SOC = np.array(charge["Charge_Capacity(Ah)"])
                    DOD = np.array(discharge["Discharge_Capacity(Ah)"])
                    print(len(SOC), len(DOD), "SOC/DOD")
                    #full cell
                    vfc = savgol_filter(charge['Voltage(V)'], 45, 2, mode='nearest')
                    vfd = savgol_filter(discharge['Voltage(V)'], 45, 2, mode='nearest')

                    if 1 < len(SOC) and len(SOC) == len(charge['Voltage(V)']):

                        charge_dq = np.gradient(SOC, vfc)
                        CFV, = self.ax6.plot(vfc, charge_dq, color=cmap.to_rgba(cycle), linewidth=0.6)
                    else:
                        CFV, = self.ax6.plot(vfc,vfc, color=cmap.to_rgba(cycle), linewidth=0.6)

                    if 1 < len(DOD) and len(DOD) == len(discharge['Voltage(V)']):

                        discharge_dq = np.gradient(DOD, vfd)
                        DFV, = self.ax6.plot(vfd, discharge_dq, color=cmap.to_rgba(cycle), linewidth=0.6)
                    else:
                        DFV, = self.ax6.plot(vfd,vfd, color=cmap.to_rgba(cycle), linewidth=0.6)

                    charge_lines.append(CFV)
                    discharge_lines.append(DFV)

                    if test.cell_type == "AuxVCell":
                    #cathode
                        vcc = savgol_filter(charge['Voltage_Cathode(V)'], 45, 2, mode='nearest')
                        vcd = savgol_filter(discharge['Voltage_Cathode(V)'], 45, 2, mode='nearest')
                        #anode
                        vac = savgol_filter(charge['Voltage_Anode(V)'], 45, 2, mode='nearest')
                        vad = savgol_filter(discharge['Voltage_Anode(V)'], 45, 2, mode='nearest')
                        try:
                            charge_anode_dq = np.gradient(SOC, vac)
                            charge_cathode_dq = np.gradient(SOC, vcc)
                            discharge_anode_dq = np.gradient(DOD, vad)
                            discharge_cathode_dq = np.gradient(DOD, vcd)

                            CAV, = self.ax6.plot(vac, charge_dq, "-.", color=cmap.to_rgba(cycle), linewidth=0.6)
                            CCV, = self.ax6.plot(vcc, charge_dq, "--", color=cmap.to_rgba(cycle), linewidth=0.6)

                            DAV, = self.ax6.plot(vad, discharge_dq, "-.", color=cmap.to_rgba(cycle), linewidth=0.6)
                            DCV, = self.ax6.plot(vcd, discharge_dq, "--", color=cmap.to_rgba(cycle), linewidth=0.6)
                        except:
                            CAV, = self.ax6.plot(vac, vac, "-.", color=cmap.to_rgba(cycle), linewidth=0.6)
                            CCV, = self.ax6.plot(vcc, vcc, "--", color=cmap.to_rgba(cycle), linewidth=0.6)

                            DAV, = self.ax6.plot(vad, vad, "-.", color=cmap.to_rgba(cycle), linewidth=0.6)
                            DCV, = self.ax6.plot(vcd, vcd, "--", color=cmap.to_rgba(cycle), linewidth=0.6)

                        charge_lines.extend([CAV, CCV])
                        discharge_lines.extend([DAV, DCV])


                self.dqdv.charge_lines[cycle + 1] = (charge_lines, vfc)
                self.dqdv.discharge_lines[cycle + 1] = (discharge_lines, vfd)

    def create_combined_plot(self, figs=[]):
        '''
        helper method to combine figures
        inputs:list of figures of type CyclesHandler, minimum 1
        creates new figure with combined data of all figures, with labels set
        according to first figure in list
        '''
        co_fig = plt.figure(FigureClass=CyclesHandler)
        ax_template = figs[0].get_axes()[0]
        ax = co_fig.add_subplot(111)
        ax.set_xlabel(ax_template.get_xlabel())
        ax.set_ylabel(ax_template.get_ylabel())

        co_fig.charge_lines = figs[1].charge_lines
        co_fig.discharge_lines = figs[1].discharge_lines
        for ind, fig in enumerate(figs):
            #iterate through each figure
            charge = fig.charge_lines
            discharge = fig.discharge_lines
            #create cycle colorbar for each figure
            max_cycle =max(len(charge), len(discharge))
            norm = matplotlib.colors.Normalize(vmin=1, vmax=max_cycle)
            cmap = matplotlib.cm.ScalarMappable(norm=norm, cmap=Seq2Colormap[ind])
            cmap.set_array([])

            colorbar = co_fig.colorbar(cmap)
            colorbar.set_label('Cycle')

            for cycle, data in charge.items():
                c = cmap.to_rgba(cycle)
                line = copy(data[0])
                line.remove()
                line.set_color(c)
                ax.add_line(line)

            for cycle, data in discharge.items():
                c = cmap.to_rgba(cycle)
                line = copy(data[0])
                line.remove()
                line.set_color(c)
                ax.add_line(line)

        return co_fig


    def toggle_aux(self):
        """turn aux data on and off"""
        try:
            alpha = plt.getp(self.ax1.cathode_line[0], "alpha")
            if alpha:
                self.ax1.cathode_line[0].set_alpha(0)
                self.ax1.anode_line[0].set_alpha(0)
            else:
                self.ax1.cathode_line[0].set_alpha(1)
                self.ax1.anode_line[0].set_alpha(1)
            self.figure.canvas.draw_idle()
        except Exception as e:
            print(e)
            pass


    def toggle_abscissa(self, axis, state, *args):
        """
        Toggle between Ah and SOC/%
        """
        for i in np.arange(self.cycle_max):
            cycle = i + 1
            d_lines = axis.discharge_lines[cycle][0]
            d_cap = axis.discharge_lines[cycle][1]

            c_lines = axis.charge_lines[cycle][0]
            c_cap = axis.charge_lines[cycle][1]

            if state == 'Ah':
                label = 'Capacity (Ah)'
                new_discharge_x = d_cap
                new_charge_x = c_cap

            elif state == 'SOC':
                label = 'SOC/DOD'
                try:
                    inverse_d_max = 1/max(d_cap)
                    inverse_c_max = 1/max(c_cap)
                except ZeroDivisionError:
                    d_max = 1 # just reset to 1 if zero division error
                    c_max = 1

                new_discharge_x = [i*inverse_d_max for i in d_cap]
                new_charge_x = [i*inverse_c_max for i in c_cap]

            for dchg, chg in zip(d_lines, c_lines):
                dchg.set_xdata(new_discharge_x)
                chg.set_xdata(new_charge_x)
        self.ax5.set_xlabel(label)
        self.ax5.relim()
        self.ax5.autoscale()


    def update_progression(self, axis, center, width):
        min = center - int(width/2)
        max = min + width

        if min < 0:
            min = 0
        else:
            pass
        if self.cycle_max < max:
            max = self.cycle_max
        else:
            pass
        for i in np.arange(self.cycle_max):
            cycle = i + 1
            if min <= cycle <= max:
                a = 1
            else:
                a = 0
            for chg, dchg in zip(axis.discharge_lines[cycle][0], axis.charge_lines[cycle][0]):
            ### chg and dchg is a list [f, a, c] of full, anode, cathode (dis)charge lines
                print(type(chg), chg, "CHG INFO")
                chg.set_alpha(a)
                dchg.set_alpha(a)

    def show(self):
        plt.show()

    def get_figure(self):
        return self.figure
