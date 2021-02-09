# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 14:02:07 2018

@author: Sean
"""

import sys
from tkinter import *
from tkinter import filedialog
import os

def get_file(*args, **kwargs):
    root = Tk()
    file = filedialog.askopenfilename()#*args, **kwargs)
    root.destroy()
    return file

import linecache

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class WinTools(object):
    def __init__(self):
        print(sys.platform)
        import win32com
        self.win32com = win32com

    def get_file(*args, **kwargs):
        root = Tk()
        file = filedialog.askopenfilename()#*args, **kwargs)
        root.destroy()
        return file

    def get_active_excel(*args, **kwargs):
        xl = selfwin32com.client.Dispatch('Excel.Application')
        wb = xl.ActiveWorkbook.FullName
        wb = xl.workbooks[1]
        return wb

class MacOSTools(object):

    def __init__(self, *args):
        print(sys.platform)
        import appscript
        self.appscript = appscript
        import subprocess
        self.subprocess = subprocess

    def get_file(self, initialdir = "/Users", **kwargs):

        initialdir = os.path.abspath(os.path.expanduser(initialdir)) + "/"
        script = """tell application "Finder"
            activate
            set strPath to POSIX file "{}"
            set theDocument to choose file with prompt "Please select a document to process:" ¬
                default location strPath
            set theDocument to POSIX path of theDocument
        end tell""".format(initialdir)

        proc = self.subprocess.Popen(['osascript', '-'],
                                stdin=self.subprocess.PIPE,
                                stdout=self.subprocess.PIPE,universal_newlines=True)
        stdout_output = proc.communicate(script)[0].strip('\n')

        return stdout_output

    def get_active_excel(self, *args, **kwargs):
        xl = self.appscript.app("Microsoft Excel")
        wb = xl.active_workbook.full_name.get()
        return wb

class OSfacade(object):
    def __init__(self, *args):
        self.platform = sys.platform
        if self.platform == 'win32':
            self.tools = WinTools()

        else:
            self.tools = MacOSTools()


    def get_file(self, initialdir=None):
        file = self.tools.get_file(initialdir)
        return file

    def get_active_excel(self, *args, **kwargs):
        wb = self.tools.get_active_excel(*args, *kwargs)
        return wb
