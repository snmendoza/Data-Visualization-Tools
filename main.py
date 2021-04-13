# S Mendoza
# created 2/23/2018


# import statements #
import data_plot
matplotlib.use('module://kivy.garden.matplotlib.backend_kivyagg')
import gui.main
from kivy.clock import Clock
if __name__ == '__main__':
    # debug = True
    # if debug:
    #     from pympler.tracker import SummaryTracker
    #     tracker = SummaryTracker()
    #     Clock.schedule_interval(tracker.print_diff, 30)
    gui.main.build_app(control_module = data_plot)
