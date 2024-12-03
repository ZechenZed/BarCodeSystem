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


def scanBarCode1(name, digit, dialog):
    barcode = simpledialog.askstring(title='Bar Code Scanning', prompt=f"Please scan the {name} barcode:")
    while len(barcode) != digit:
        barcode = simpledialog.askstring(title='Bar Code Scanning', prompt=f"Please scan the {name} barcode:")
    return barcode


def scanBarCode2(name, digit):
    barcode = input(f"Bar Code Scanning {name} barcode:")
    while len(barcode) != digit:
        print("Please scann the CORRECT barcode!")
        barcode = input(f"Bar Code Scanning {name} barcode:")
    print("\n")
    return barcode


def time_correct(end_time_local, start_time_local):
    cost_hour = end_time_local.tm_hour - start_time_local.tm_hour
    cost_min = end_time_local.tm_min - start_time_local.tm_min
    cost_sec = end_time_local.tm_sec - start_time_local.tm_sec
    if cost_sec < 0:
        cost_sec = 60 - abs(cost_sec)
        cost_min -= 1
    if cost_min < 0:
        cost_min = 60 - abs(cost_min)
        cost_hour -= 1
    if cost_hour < 0:
        cost_hour = 24 - abs(cost_hour)
    return cost_hour, cost_min, cost_sec


def scanWorkOrder():
    workOrder_Digit = 4
    workOrder = scanBarCode2("Work Order", workOrder_Digit)
    return workOrder


def scanCell():
    cell_digit = 5
    cell = scanBarCode2("Cell", cell_digit)

    while not ("G" in cell or "E" in cell):
        cell = scanBarCode2("Cell", cell_digit)
    return cell


def scanEmployeeID():
    numOfPPL = 0
    identifier = True
    while identifier:
        print("Please Type in a number no more than 7!")
        while True:
            numOfPPL = input('How many people will be working in this assembly today:')
            try:
                numOfPPL = int(numOfPPL)
                if numOfPPL < 7:
                    identifier = False
                break
            except ValueError:
                print("Please type in a number")

    employeeIDs = [0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(numOfPPL):
        while True:
            workID_digit = 5
            employeeID = scanBarCode2("Employee ID", workID_digit)
            while "E" in employeeID or "G" in employeeID:
                print("Please Scan the CORRECT Employee ID")
                employeeID = scanBarCode2("Employee ID", workID_digit)
            if employeeID in employeeIDs:
                print("Please Scan a DIFFERENT ID!")
            else:
                employeeIDs[i] = employeeID
                break
    return employeeIDs, numOfPPL


def scanAssembly():
    assembly_digit = 16
    assembly = scanBarCode2("Assembly", assembly_digit)
    print("Please grab your part and start working, stay safe")
    holder = scanBarCode2("Assembly (when you finish)", assembly_digit)
    while holder != assembly:
        print("Please scan the right Assembly Number!")
        holder = scanBarCode2("Assembly (when you finish)", assembly_digit)
    return assembly


def logRevision(workOrder, assembly, cell, numOfPPL, employeeIDs, start, end):
    df = pd.read_excel('WorkLog.xlsx', sheet_name='Sheet1')
    df = pd.DataFrame(df)
    last_non_empty_row = df.last_valid_index()

    if not last_non_empty_row and last_non_empty_row != 0:
        writing_row = 0
    else:
        writing_row = last_non_empty_row + 1

    start = start[1]
    end = end[1]

    # Writing
    df.loc[writing_row, ['Work Order', 'Assembly', 'Cell']] = [workOrder, assembly, cell]
    df.loc[writing_row, ['Time Start Date', 'Time Start', 'Time End Date', 'Time End']] = \
        [f"{start.tm_year}/{start.tm_mon}/{start.tm_mday}", f"{start.tm_hour}:{start.tm_min}:{start.tm_sec}",
         f"{end.tm_year}/{end.tm_mon}/{end.tm_mday}", f"{end.tm_hour}:{end.tm_min}:{end.tm_sec}"]

    for i in range(numOfPPL):
        df.loc[writing_row, [f'Employee ID{i + 1}']] = employeeIDs[i]

    with pd.ExcelWriter('WorkLog.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

        workbook = writer.book
        worksheet = workbook['Sheet1']

        fixed_width = 20
        for col in worksheet.columns:
            column_letter = col[0].column_letter
            worksheet.column_dimensions[column_letter].width = fixed_width


def continuous_scanning():
    # Time
    year = time.localtime().tm_year
    month = time.localtime().tm_mon
    day = time.localtime().tm_mday
    log = []

    print("Please start scanning now.")
    while True:
        info = input()
        if "End of the day." in info:
            print("Enjoy the rest of the day!")
            break
        elif "Report" in info:
            logRevision()
        else:
            info_time = time.localtime()
            info_pack = [info, info_time]
            log += [info_pack]

    read_data = {}


def main():
    print("Please make sure the WorkLog Excel is close during ANYTIME of scanning")
    workOrder = scanWorkOrder()
    cell = scanCell()
    employeeIDs, numOfPPL = scanEmployeeID()
    start = [time.time(), time.localtime(time.time())]
    assembly = scanAssembly()
    end = [time.time(), time.localtime(time.time())]

    cost_hour, cost_min, cost_sec = time_correct(end[1], start[1])
    print(f"Congrats, You finished the work and the cost time is {cost_hour} hrs, {cost_min} mins, {cost_sec} secs")

    logRevision(workOrder, assembly, cell, numOfPPL, employeeIDs, start, end)

    print("Press ESC to exit the program.")
    while True:
        if keyboard.is_pressed("esc"):
            print("ESC pressed, exiting...")
            break


def normalize_list_by_length_final(input_list, default_value='X'):
    # 定义长度与类别的映射
    length_to_category = {7: 'A', 8: 'B', 14: 'C'}
    target_frame = ['A', 'B', 'C']  # 目标框架
    normalized_list = []
    temp_frame = {key: default_value for key in target_frame}  # 初始化临时框架

    for item in input_list:
        # 根据长度判断类别
        category = length_to_category.get(len(item))
        if category and temp_frame[category] == default_value:
            temp_frame[category] = item
        # 当收集到完整的 [A, B, C] 组合时，将其追加到结果中
        if all(temp_frame[key] != default_value for key in target_frame):
            normalized_list.extend(temp_frame.values())
            temp_frame = {key: default_value for key in target_frame}  # 重置框架

    # 处理未完成的部分（无论是否完整）
    normalized_list.extend(temp_frame.values())

    return normalized_list


if __name__ == '__main__':
    #main()
    # continuous_scanning()
    input = ["ID111211", "ID112345", "ID19823", "ID192837", 'ID112381298371']
    default_value = '-'
    result = normalize_list_by_length_final(input, default_value)
    print(result)
