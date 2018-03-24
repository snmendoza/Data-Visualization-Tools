# my_module.py
import os
import xlwings as xw

def my_macro():
    wb = xw.Book.caller()
    print(wb.fullname)
    help(wb)

if __name__ == '__main__':
    # Expects the Excel file next to this source file, adjust accordingly.
    my_macro()
