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

from pandas.core.window.doc import template_see_also

year = time.localtime().tm_year
month = time.localtime().tm_mon
day = time.localtime().tm_mday


def time_correct(start_hour, start_min, end_hour, end_min):
    cost_hour = end_hour - start_hour
    cost_min = end_min - start_min
    if cost_min < 0:
        cost_min = 60 - abs(cost_min)
        cost_hour -= 1
    if cost_hour < 0:
        cost_hour = 24 - abs(cost_hour)
    return cost_hour * 60 + cost_min


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
        if len(temp_work[0]) == 15:
            temp_work_pack = list(temp_work[1])
            temp_stat = temp_work[0][3:6]
            temp_work_pack.insert(0, temp_stat)
            log_dict[temp_sale[0]][temp_employee[0]][temp_work[0][7:]].append(temp_work_pack)
        else:
            log_dict[temp_sale[0]][temp_employee[0]][temp_work[0]].append(temp_work[1])

    with open(f"{year}_{month}_{day}_WorkLog.json", 'w') as json_file:
        json.dump(log_dict, json_file, indent=6, separators=(", ", " : "))
    return log_dict


def main():
    input_data = continuous_scanning()
    input_data_fixed = missing_data_processing(input_data)
    input_data_fixed_dict = list_to_dic(input_data_fixed)
    pprint.pprint(input_data_fixed_dict)

    # Create the structure for later transformation to pandas data structure.
    line_count = len(input_data_fixed) // 3
    template = np.zeros((line_count, 18)).astype(str)
    print("Start Data Processing")

    for SO_key in input_data_fixed_dict:
        print(f"Processing {SO_key}")
        for employee_key in input_data_fixed_dict[SO_key]:
            print(f"    Processing {employee_key}")
            for workid_key in input_data_fixed_dict[SO_key][employee_key]:
                print(f"        Processing {workid_key}")
                temp_time_list = input_data_fixed_dict[SO_key][employee_key][workid_key]

                start_end_error = False if len(temp_time_list) % 2 == 0 else True
                for i in range(len(temp_time_list)):
                    if i % 2 == 0:
                        if temp_time_list[i][0] != "STA":
                            start_end_error = True
                            break
                    else:
                        if temp_time_list[i][0] != "END":
                            start_end_error = True
                            break

                # if any of the data is missing
                if SO_key == "-" or employee_key == "-" or workid_key == "-" or start_end_error:
                    row = np.where(template[:, 12] == "0.0")[0][0]
                    template[row, 0] = SO_key
                    template[row, 2] = workid_key
                    template[row, 3] = employee_key

                    for j in range(len(temp_time_list)):
                        temp_time = temp_time_list[j]
                        if temp_time != "-":
                            if "END" in temp_time[0]:
                                template[row, 10] = 1
                                template[row, 13] = f"{temp_time[1]}/{temp_time[2]}/{temp_time[3]}"
                                template[row, 14] = f"{temp_time[4]}:{temp_time[5]}"
                            else:
                                template[row, 10] = 1
                                template[row, 11] = f"{temp_time[1]}/{temp_time[2]}/{temp_time[3]}"
                                template[row, 12] = f"{temp_time[4]}:{temp_time[5]}"
                        template[row, 17] = "Miss Data"
                else:
                    rows = np.where(template == SO_key)[0]
                    row = np.where(template[rows] == workid_key)[0]
                    print(len(template[row]))
                    # Has the record before.
                    if len(template[row]) != 0:
                        # decide the location for the new employee
                        temp_new_employee_ind = np.where(template[row[0]][3:11] == "0.0")[0][0]
                        template[row, temp_new_employee_ind] = employee_key

                        cost_min_tt = 0
                        # Go through all the valid time stamp that employee has
                        for j in range(0, len(temp_time_list), 2):
                            temp_date_start = f"{temp_time_list[j][1]}/{temp_time_list[j][2]}/{temp_time_list[j][3]}"
                            temp_time_start = f"{temp_time_list[j][4]}:{temp_time_list[j][5]}"
                            temp_date_end = (f"{temp_time_list[j + 1][1]}/{temp_time_list[j + 1][2]}"
                                             f"/{temp_time_list[j + 1][3]}")
                            temp_time_end = f"{temp_time_list[j + 1][4]}:{temp_time_list[j + 1][5]}"

                            # Cost time in min
                            cost_min_tt += time_correct(temp_time_list[j][4], temp_time_list[j][5],
                                                        temp_time_list[j + 1][4],temp_time_list[j + 1][5])

                            # Compare to see if the start time is the earliest start time.
                            if template[row, 11] > temp_date_start:
                                template[row, 11] = temp_date_start
                                template[row, 12] = temp_time_start
                            elif template[row, 11] == temp_date_start:
                                if template[row, 12] > temp_time_start:
                                    template[row, 12] = temp_time_start

                            # Compare to see if the end time is the latest start time.
                            if template[row, 13] < temp_date_end:
                                template[row, 13] = temp_date_end
                                template[row, 14] = temp_time_end
                            elif template[row, 13] == temp_date_end:
                                if template[row, 14] < temp_time_end:
                                    template[row, 14] = temp_time_end
                        print(type(template[row,16][0]), template[row,16],type(template[row,16][0]))
                        template[row, 16] = (int(int(template[row, 16]) * int(template[row, 10]) + cost_min_tt) /
                                             (int(template[row, 10]) + 1))
                        template[row, 10] = int(template[row,10]) + 1

                    # Does not have the record before.
                    else:
                        row = np.where(template[:, 12] == "0.0")[0][0]
                        template[row, 0] = SO_key
                        template[row, 2] = workid_key
                        template[row, 3] = employee_key
                        template[row, 10] = 1
                        cost_min_tt = 0
                        for j in range(0, len(temp_time_list), 2):

                            temp_date_start = f"{temp_time_list[j][1]}/{temp_time_list[j][2]}/{temp_time_list[j][3]}"
                            temp_time_start = f"{temp_time_list[j][4]}:{temp_time_list[j][5]}"
                            temp_date_end = (f"{temp_time_list[j + 1][1]}/{temp_time_list[j + 1][2]}"
                                             f"/{temp_time_list[j + 1][3]}")
                            temp_time_end = f"{temp_time_list[j + 1][4]}:{temp_time_list[j + 1][5]}"

                            cost_min_tt += time_correct(temp_time_list[j][4], temp_time_list[j][5],
                                                        temp_time_list[j + 1][4],
                                                        temp_time_list[j + 1][5])

                            # Compare to see if the start time is the earliest start time.
                            if template[row, 11] > temp_date_start:
                                template[row, 11] = temp_date_start
                                template[row, 12] = temp_time_start
                            elif template[row, 11] == temp_date_start:
                                if template[row, 12] > temp_time_start:
                                    template[row, 12] = temp_time_start
                            elif template[row,11] == "0.0":
                                template[row, 11] = temp_date_start
                                template[row, 12] = temp_time_start

                            # Compare to see if the end time is the latest start time.
                            if template[row, 13] < temp_date_end:
                                template[row, 13] = temp_date_end
                                template[row, 14] = temp_time_end
                            elif template[row, 13] == temp_date_end:
                                if template[row, 14] < temp_time_end:
                                    template[row, 14] = temp_time_end
                            elif template[row,13] == "0.0":
                                template[row, 13] = temp_date_end
                                template[row, 14] = temp_time_end

                        template[row, 16] = cost_min_tt

    print(template)


if __name__ == '__main__':
    main()
