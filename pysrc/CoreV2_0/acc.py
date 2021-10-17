
'''
Author: xv_rong
Date: 2021-10-13 15:08:27
LastEditors: xv_rong
LastEditTime: 2021-10-17 19:34:42
Description: 
FilePath: /RFID_FMS/pysrc/CoreV2_0/acc.py
'''


import os
import copy
import core_v
from plot_result import *
from main import *


PLOT_EPC = '2d-3b'
TEST_EPC = '2d-3b'
RIGHT_ORDER = ['3B', '3A', '39', '38', '37', '36', '35',
               '34', '33', '32', '31', '30', '2F', '2E', '2D']
RE_RIGHT_ORDER = copy.deepcopy(RIGHT_ORDER)
RE_RIGHT_ORDER.reverse()
TEST_DIR = r'Data/2021-10-13/立放'

# PLOT_EPC = '1e-2c'
# TEST_EPC = '1e-2c'
# RIGHT_ORDER = ['1E', '1F', '20', '21', '22', '23', '24',
#                '25', '26', '27', '28', '29', '2A', '2B', '2C']
# RE_RIGHT_ORDER = copy.deepcopy(RIGHT_ORDER)
# RE_RIGHT_ORDER.reverse()
# TEST_DIR = r'Data/2021-10-13/立放'


TEST_ANTENNA = '1,9'
SHOW_FIG = False
SAVE_FIG = False
FIG = False


def get_order(epc=TEST_EPC, test_file=TEST_FILE, plot_epc=PLOT_EPC):
    TEST_EPC = epc
    TEST_FILE = test_file
    PLOT_EPC = plot_epc
    ori_epc, ori_time, ori_phase, __ = ObtainData(
        TEST_EPC, filename=TEST_FILE, antenna=TEST_ANTENNA)
    plot_epc, __, __, __ = ObtainData(
        PLOT_EPC, filename=TEST_FILE, antenna=TEST_ANTENNA)

    fit_epc, core_time, core_phase, unfit_epc = process(
        ori_epc, ori_time, ori_phase)

    fit_phase, parameter = get_fit(fit_epc, core_time, core_phase)

    pos, order = sort_epc(fit_epc, parameter)
    if FIG:
        plot_order(test_file, plot_epc, fit_epc, core_time, core_phase,
                   fit_phase, ori_time, ori_phase, pos, order, parameter, unfit_epc, SHOW_FIG, SAVE_FIG)

    return order


def main():
    right = 0
    wrong = 0
    len = 0
    data_file = os.listdir(TEST_DIR)

    wrong = 0
    right = 0
    len = 0
    for file in data_file:
        if not file.endswith('txt') or file == '14-43-53.txt':
            continue
        len += 1
        order = get_order(epc=TEST_EPC, test_file=TEST_DIR +
                          '/' + file, plot_epc=PLOT_EPC)
        if order == RIGHT_ORDER or order == RE_RIGHT_ORDER:
            right += 1
            # print('right')
        else:
            print(file)
            wrong += 1
            print('wrong')
    print("ACC:" + str(right / len))


if __name__ == '__main__':
    main()
