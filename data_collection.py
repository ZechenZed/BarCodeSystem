import time
import tkinter as tk
from tkinter import simpledialog
import keyboard
import sys
import json
import numpy as np
from collections import defaultdict
import pandas as pd
import pprint
import json
year = time.localtime().tm_year
month = time.localtime().tm_mon
day = time.localtime().tm_mday

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


# def logRevision(excel_data):
#     year = time.localtime().tm_year
#     month = time.localtime().tm_mon
#     day = time.localtime().tm_mday
#     with pd.ExcelWriter(f'{year}_{month}_{day}_WorkLog.xlsx', engine='xlsxwriter') as writer:


def continuous_scanning():
    # Time

    log = []

    print("Please start scanning now.")
    while True:
        info = input()
        if "End of the day." in info:
            print("Enjoy the rest of the day!")
            break
        else:
            info_time = time.localtime()[0:6]
            info_pack = [info, info_time]
            log += [info_pack]

    return log


def missing_data_processing(data):
    i = 0
    while i < len(data):
        if len(data[i][0]) != 7:
            data.insert(i, ["-", "-"])
        try:
            if len(data[i + 1][0]) != 8:
                data.insert(i + 1, ["-", "-"])
        except IndexError:
            data.insert(len(data), ["-", "-"])
        try:
            if len(data[i + 2][0]) != 15:
                data.insert(i + 2, ["-", "-"])
        except IndexError:
            data.insert(len(data), ["-", "-"])
            break
        i += 3
    return data


def list_to_dic(input_list):
    log_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for i in range(0, len(input_list), 3):
        temp_sale = input_list[i]
        temp_employee = input_list[i + 1]
        temp_work = input_list[i + 2]
        log_dict[temp_sale[0]][temp_employee[0]][temp_work[0]].extend(temp_work[1])
    with open(f"{year}_{month}_{day}_WorkLog.json", 'w') as json_file:
        json.dump(log_dict, json_file,indent=6,separators=(", "," : "))
        # if temp_sale[0] in log_dict:
        #     if temp_employee[0] in log_dict[temp_sale[0]]:
        #         log_dict[temp_sale[0]][temp_employee[0]][temp_work[0]].extend([temp_work[1]])
        #     else:
        #         log_dict[temp_sale[0]][temp_employee[0]][temp_work[0]] = [temp_work[1]]
        # else:
        #     log_dict[temp_sale[0]][temp_employee[0]][temp_work[0]] = [temp_work[1]]
    return log_dict


def main():
    input_data = continuous_scanning()
    input_data_fixed = missing_data_processing(input_data)
    input_data_fixed_dict = list_to_dic(input_data_fixed)
    pprint.pprint(input_data_fixed_dict)
    # line_count = len(input_data_fixed)//3
    # template = np.zeros((line_count,18))
    # for i in range(0,line_count,3):
    #     temp = template[np.where(template == input_data_fixed[i])]
    #     if not len(temp):
    #         temp = template[np.where(temp == input_data_fixed[i+1])]
    #     else:
    #         first_empty_line = list(np.where(template[:,0] == 0))[0]
    #         template[first_empty_line][0] = input_data_fixed[i]
    #         template[first_empty_line][2] = input_data_fixed[i+2]
    #         template[first_empty_line][3] = input_data_fixed[i+1]

    # data_frame = np.array([[1, 2], [1, 4], [5, 6]])
    # # filter = data_frame[np.where(data_frame[np.where(data_frame == 0)[0]] == 4)[0]]
    # test = list(np.where(data_frame == 0))[0]
    # if len(test):
    #     print(1)
    # # print(filter)


if __name__ == '__main__':
    main()
