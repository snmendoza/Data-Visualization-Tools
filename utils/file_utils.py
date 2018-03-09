# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 14:02:07 2018

@author: Sean
"""

import sys
from tkinter import *
from tkinter import filedialog

def get_file(*args):
    root = Tk()
    file = filedialog.askopenfilename(*args)
    root.destroy()
    return file