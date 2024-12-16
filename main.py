import time
import keyboard
import sys
import json
import numpy as np
from collections import defaultdict
import pandas as pd
import pprint
import json
from openpyxl import load_workbook

# Define some of the global variables
year = time.localtime().tm_year
month = time.localtime().tm_mon
day = time.localtime().tm_mday

len_employeeID = int(3)  # Sample Employee ID: 001
len_work_ID = int(len_employeeID + 11)  # Hard coded to 15 for len_employeeID == 14
len_SO = int(len_employeeID + 4)  # Hard Coded to 7 for len_employeeID == 3


def time_correct(start_hour, start_min, end_hour, end_min):
    cost_hour = end_hour - start_hour
    cost_min = end_min - start_min
    if cost_min < 0:
        cost_min = 60 - abs(cost_min)
        cost_hour -= 1
    if cost_hour < 0:
        cost_hour = 24 - abs(cost_hour)
    return cost_hour * 60 + cost_min


def where_row(temp_list, column, value):
    where_row_rows = []
    for where_row_row in range(len(temp_list)):
        if temp_list[where_row_row][column] == value:
            where_row_rows.append(where_row_row)
            if value == 0:
                return where_row_rows
    return where_row_rows


def where_column(temp_list_line, value):
    for column in range(len(temp_list_line)):
        if temp_list_line[column] == value:
            return column


def continuous_scanning():
    log = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    print("Please start scanning now.")

    while True:
        info = input()
        if "End of the day." in info:
            print("Enjoy the rest of the day!")
            break
        # timer for 90 min tempo. --Skylar

        else:
            info_time = time.localtime()[3:5]
            info_pack = [info, info_time]  # Pack the data with the corresponding time.
            log[int(info[0:3])] += [info_pack]  # Use the ID prefix from the bar code scanner to sort the input data.

    # Flatten the log list
    log = [item for sublist in log for item in sublist]

    print("Scanning Ended")
    return log


def data_processing(log):
    print("Processing missing data.")
    # pointer index
    i = 0

    # if the first item in dats does not have a len of 8, replace the item with a 1D list
    if len(log[i][0]) != 7:
        log.insert(0, ['Missing Unit Number', '-'])

    # Move to the index 1
    i += 1

    # loop through every STA-END tuple in the list
    while i < len(log):
        # if the second item in log does not start with STA, replace the item with a 1D list
        if "STA" not in log[i][0]:
            log.insert(i, ['Missing Start Time', '-'])

        # # if the second item in log does not start with STA, replace the item with a 1D list
        # if "STA" not in log[i+1]:
        #     # if it starts with END, 1) use the time for scanning the unit number, 2)
        #     if len(log[i + 2][4:6]) != "STA":
        #         # TODO
        #         pass
        #     else:
        #         log.insert(1, ['Missing Start Time', '-'])

        # if the third item in log does not start with END, replace the item with a 1D list
        try:  # Use try-except to handle the IndexError but still add the placeholder for the missing data
            if "END" not in log[i + 1][0]:
                log.insert(i + 1, ['Missing End Time', '-'])
        except IndexError:
            log.insert(len(log), ['Missing End Time', '-'])

        # # if the third item in log does not start with END, replace the item with a 1D list
        # if len(log[i+2][4:6]) != "END":
        #     # if it starts with STA, Trigger warning to PM/ VPM
        #     if len(log[i + 2][4:6]) != "STA":
        #         # TODO
        #         pass
        #     else:
        #         log.insert(2, ['Missing End Time', '-'])

        # increment pointer index
        i += 2

    print('Missing log fixed.')
    return log

    # # Corner case 1: Have STA No END, Have STA for next job already --> Trigger warning to PM / VPM.
    # # Corner case 2: No STA Have END, 1) index 0's job use the time for scanning the PO, 2) Use
    #
    # # loop through every item in the log list
    # while i < len(log):
    #     # if the first item in log does not have a len of 8, replace the entire item with a 1D list
    #     if len(log[i][0]) != len_SO:
    #         log.insert(i, ["-", "-"])
    #     try:
    #         # if the second item in log does not have a len of 4, replace the entire item with a 1D list
    #         if len(log[i + 1][0]) != len_employeeID:
    #             log.insert(i + 1, ["-", "-"])
    #     except IndexError:
    #         log.insert(len(log), ["-", "-"])
    #     try:
    #         # if the third item in log does not have a len of 15, replace the entire item with a 1D list
    #         if len(log[i + 2][0]) != len_work_ID:
    #             log.insert(i + 2, ["-", "-"])
    #     except IndexError:
    #         log.insert(len(log), ["-", "-"])
    #         break
    #
    #     # increment pointer index
    #     i += 3
    # print('Missing log fixed.')
    # return log


def list_to_dic(input_list):
    print('Start to put in dictionary')
    # Create a dictionary with defaultdict to handle some null error.
    log_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # First index of the input list should be the SO
    temp_SO = input_list[0][0]

    # Loop through the rest of the input list
    for i in range(1, len(input_list), 2):
        # Choose employee id & job id based on the STA / END
        if input_list[i][0] != "-":
            temp_employee = input_list[i][0][0:3]  # 001
            temp_work = input_list[i][0][8:]  # eg.  EMM0029
        else:
            temp_employee = input_list[i+1][0][0:3]
            temp_work = input_list[i+1][0][8:]

        # STA work pack
        temp_work_STA_pack = list(input_list[i][1])  # Start time
        temp_work_STA_pack.insert(0, "STA")

        # End Work Pack
        temp_work_END_pack = list(input_list[i+1][1])  # End time
        temp_work_END_pack.insert(0, "END")

        log_dict[temp_SO][temp_employee][temp_work].append(temp_work_STA_pack)
        log_dict[temp_SO][temp_employee][temp_work].append(temp_work_END_pack)


        # # Check if we have the valid time stamp to put into the dict.
        # if len(temp_work[0]) == len_work_ID:
        #     temp_work_pack = list(temp_work[1])
        #     temp_work_pack.insert(0, temp_work[0][4:7])
        #     log_dict[temp_sale[0]][temp_employee[0]][temp_work[0][8:]].append(temp_work_pack)
        # else:
        #     log_dict[temp_sale[0]][temp_employee[0]][temp_work[0]].append(temp_work[1])

    # Store the original data into json file for later use.
    with open(f"{year}_{month}_{day}_WorkLog.json", 'w') as json_file:
        json.dump(log_dict, json_file, indent=6, separators=(", ", " : "))

    print("Finished with dictionary.")
    return log_dict


def detect_missing_data(current_values):
    # Detect part of the error cases
    start_end_error = False if len(current_values) % 2 == 0 else True

    # loop through all the values
    for i in range(len(current_values)):
        if current_values[i][1] == "-":
            start_end_error = True
            break

    return start_end_error


def update_time(template, row, temp_date_start, temp_time_start, temp_date_end, temp_time_end):
    # Compare to see if the start time is the earliest start time.
    if template[row][11] == 0:
        template[row][11] = temp_date_start
        template[row][12] = temp_time_start
    if template[row][11] > temp_date_start:
        template[row][11] = temp_date_start
        template[row][12] = temp_time_start
    elif template[row][11] == temp_date_start:
        if template[row][12] > temp_time_start:
            template[row][12] = temp_time_start

    # Compare to see if the end time is the latest start time.
    if template[row][13] == 0:
        template[row][13] = temp_date_start
        template[row][14] = temp_time_start
    if template[row][13] < temp_date_end:
        template[row][13] = temp_date_end
        template[row][14] = temp_time_end
    elif template[row][13] == temp_date_end:
        if template[row][14] < temp_time_end:
            template[row][14] = temp_time_end
    return template


def duration_time(template, row):
    sta_hour_ind = 1 if len(template[row][12]) % 2 == 0 else 2
    end_hour_ind = 1 if len(template[row][14]) % 2 == 0 else 2

    template[row][15] = time_correct(int(template[row][12][0:sta_hour_ind]),
                                     int(template[row][12][sta_hour_ind + 1:]),
                                     int(template[row][14][0:end_hour_ind]),
                                     int(template[row][14][end_hour_ind + 1:]))
    return template


def writing_excel(input_data_fixed_dict, line_count):
    # Create the data structure as following:
    # 0: Work Order#, 1: Cell#, 2: Task#, 3: EmployeeID1#, 4: EmployeeID2#, 5: EmployeeID3#, 6: EmployeeID4#,
    # 7: EmployeeID5#, 8: EmployeeID6#, 9: EmployeeID7#, 10: Number of Operators, 11: Time start date, 12: Time start,
    # 13: Time end date, 14: Time end, 15: Duration time, 16: Average time consumed per operator, 17: Missed Data?

    template = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    for ct in range(line_count - 1):
        template.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    print("Start Data Processing")

    for SO_key in input_data_fixed_dict:
        print(f"Processing {SO_key}")

        for employee_key in input_data_fixed_dict[SO_key]:
            print(f"    Processing {employee_key}")

            for workid_key in input_data_fixed_dict[SO_key][employee_key]:
                print(f"        Processing {workid_key}")

                # Current value(s) for the key.
                temp_time_list = input_data_fixed_dict[SO_key][employee_key][workid_key]

                start_end_error = detect_missing_data(temp_time_list)

                # if any of the data is missing
                if SO_key == "-" or employee_key == "-" or workid_key == "-" or start_end_error:

                    # Write those missing data into new lines
                    for j in range(len(temp_time_list)):
                        row = where_row(template, 10, 0)[0]  # Find the next non-occupied row

                        # Assign the values
                        template[row][0] = SO_key
                        template[row][2] = workid_key
                        template[row][3] = employee_key
                        template[row][10] = 1

                        # Current work pack: Either start or end
                        temp_time = temp_time_list[j]
                        if temp_time[1] != "-":
                            if "END" in temp_time[0]:
                                template[row][13] = f"{year}/{month}/{day}"
                                template[row][14] = f"{temp_time[1]}:{temp_time[2]}"
                            else:
                                template[row][11] = f"{year}/{month}/{day}"
                                template[row][12] = f"{temp_time[1]}:{temp_time[2]}"

                        template[row][17] = "Miss Data"

                # If no data missing
                else:
                    SO_rows = where_row(template, 0, SO_key)

                    row = 0
                    if len(SO_rows) == 0:
                        row = None
                    elif len(SO_rows) == 1:
                        workid_rows = SO_rows[0]
                        if template[workid_rows][2] == workid_key:
                            if template[workid_rows][17] == "Miss Data":
                                row = None
                            else:
                                row = workid_rows
                        else:
                            row = None
                    else:
                        workid_rows = where_row(template[SO_rows[0]:SO_rows[len(SO_rows) - 1]], 2, workid_key)
                        if len(workid_rows) == 0:
                            row = None
                        elif len(workid_rows) == 1:
                            if template[workid_rows[0]][17] == "Miss Data":
                                row = None
                            else:
                                row = workid_rows[0]
                        else:
                            row = None

                    # Has the record before, we then update it with the new data.
                    if row is not None:
                        # decide the indexing for the new employee
                        if employee_key not in template[row][3:11]:
                            temp_new_employee_ind = where_column(template[row][3:11], 0)
                            template[row][temp_new_employee_ind + 3] = employee_key

                        cost_min_tt = 0

                        # Go through all the valid time stamp that employee has
                        for j in range(0, len(temp_time_list), 2):
                            temp_date_start = f"{year}/{month}/{day}"
                            temp_time_start = f"{temp_time_list[j][1]}:{temp_time_list[j][2]}"
                            temp_date_end = f"{year}/{month}/{day}"
                            temp_time_end = f"{temp_time_list[j + 1][1]}:{temp_time_list[j + 1][2]}"

                            # Cost time in min
                            cost_min_tt += time_correct(temp_time_list[j][1], temp_time_list[j][2],
                                                        temp_time_list[j + 1][1], temp_time_list[j + 1][2])

                            template = update_time(template, row, temp_date_start, temp_time_start, temp_date_end,
                                                   temp_time_end)

                        template[row][16] = (template[row][16] * template[row][10] + cost_min_tt) / (
                                template[row][10] + 1)
                        template[row][10] += 1

                        template = duration_time(template, row)

                    # Does not have the record before.
                    else:
                        row = where_row(template, 12, 0)[0]
                        template[row][0] = SO_key
                        template[row][2] = workid_key
                        template[row][3] = employee_key
                        template[row][10] = 1
                        cost_min_tt = 0
                        for j in range(0, len(temp_time_list), 2):
                            temp_date_start = f"{year}/{month}/{day}"
                            temp_time_start = f"{temp_time_list[j][1]}:{temp_time_list[j][2]}"
                            temp_date_end = f"{year}/{month}/{day}"
                            temp_time_end = f"{temp_time_list[j + 1][1]}:{temp_time_list[j + 1][2]}"

                            cost_min_tt += time_correct(temp_time_list[j][1], temp_time_list[j][2],
                                                        temp_time_list[j + 1][1],
                                                        temp_time_list[j + 1][2])

                            template = update_time(template, row, temp_date_start, temp_time_start, temp_date_end,
                                                   temp_time_end)

                        template[row][16] = cost_min_tt
                        template = duration_time(template, row)

    df_template = pd.DataFrame(template, columns=['Work Order', 'Cell#', 'Task', 'EmployeeID1', 'EmployeeID2',
                                                  'EmployeeID3', 'EmployeeID4', 'EmployeeID5', 'EmployeeID6',
                                                  'EmployeeID7', 'Number of Operators', 'Time start date', 'Time start',
                                                  'Time end date', 'Time end', 'Duration time',
                                                  'Average time consumed per operator', 'Missed Data'])
    print(df_template)
    log_file_name = f'{year}{month}{day}_log.xlsx'
    df_template.to_excel(log_file_name, index=False)

    # Formatting of the file
    workbook = load_workbook(log_file_name)
    worksheet = workbook.active

    for col in worksheet.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = max_length + 2
        worksheet.column_dimensions[col_letter].width = adjusted_width

    workbook.save(log_file_name)


def main():
    input_data = continuous_scanning()
    input_data_fixed = data_processing(input_data)
    input_data_fixed_dict = list_to_dic(input_data_fixed)
    # pprint.pprint(input_data_fixed_dict)
    writing_excel(input_data_fixed_dict, (len(input_data_fixed)-1))


if __name__ == '__main__':
    main()
