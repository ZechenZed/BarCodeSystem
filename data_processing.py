import time
import tkinter as tk
from tkinter import simpledialog
import keyboard
import sys
import json
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget, \
    QInputDialog
import pandas as pd


def json_reading():
    year = time.localtime().tm_year
    month = time.localtime().tm_mon
    day = time.localtime().tm_mday
    with open(f"log{year}{month}{day}.txt", "r",encoding="utf-8") as f:
        data = f.read()
    print(type(data))

    df = pd.read_excel('WorkLog.xlsx', sheet_name='Sheet1')
    df = pd.DataFrame(df)
    last_non_empty_row = df.last_valid_index()

    if not last_non_empty_row and last_non_empty_row != 0:
        writing_row = 0
    else:
        writing_row = last_non_empty_row + 1

     # for i in range(len())

    # Writing
    # df.loc[writing_row, ['Work Order', 'Assembly', 'Cell']] = [workOrder, assembly, cell]
    # df.loc[writing_row, ['Time Start Date', 'Time Start', 'Time End Date', 'Time End']] = \
    #     [f"{start.tm_year}/{start.tm_mon}/{start.tm_mday}", f"{start.tm_hour}:{start.tm_min}:{start.tm_sec}",
    #      f"{end.tm_year}/{end.tm_mon}/{end.tm_mday}", f"{end.tm_hour}:{end.tm_min}:{end.tm_sec}"]
    #
    # for i in range(numOfPPL):
    #     df.loc[writing_row, [f'Employee ID{i + 1}']] = employeeIDs[i]
    #
    # with pd.ExcelWriter('WorkLog.xlsx', engine='openpyxl') as writer:
    #     df.to_excel(writer, index=False, sheet_name='Sheet1')
    #
    #     workbook = writer.book
    #     worksheet = workbook['Sheet1']
    #
    #     fixed_width = 20
    #     for col in worksheet.columns:
    #         column_letter = col[0].column_letter
    #         worksheet.column_dimensions[column_letter].width = fixed_width


if __name__ == '__main__':
    json_reading()
