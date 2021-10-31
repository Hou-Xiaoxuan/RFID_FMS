'''
Author: xv_rong
Date: 2021-09-23 20:54:21
LastEditors: xv_rong
LastEditTime: 2021-10-31 15:02:35
Description: 一个数据量增大后的版本
FilePath: /RFID_FMS/pysrc/CoreV2_0/main.py
'''

from matplotlib.pyplot import plot
from ManageData.ObtainData import ObtainData
from CoreV2_0.core_v import core_v
from CoreV2_0.core_v import regression
from CoreV2_0.plot_result import plot_order


# PLOT_EPC = '35-36'
# TEST_EPC = '35-36'

# PLOT_EPC = '2d-3b'
# TEST_EPC = '2d-3b'
PLOT_EPC = '1e-2c'
TEST_EPC = '1e-2c'
# PLOT_EPC = '08-0D'
# TEST_EPC = '08-0D'
TEST_ANTENNA = '1'
TEST_FILE = 'Data/2021-10-31/14-31-46.txt'
SHOW_FIG = True
SAVE_FIG = False


def get_fit(epc, time, phase):
    fit_phase = []
    parameter = []
    ori_pos = []
    for i in range(len(epc)):
        [tmp_fit_phase, tmp_parameter] = regression(
            time[i], phase[i], 2)
        fit_phase.append(tmp_fit_phase)
        parameter.append(tmp_parameter)
        ori_pos.append(-tmp_parameter[1] / (2 * tmp_parameter[0]))
    return fit_phase, parameter


def sort_epc(epc, parameter):
    pos = []
    for i in range(len(parameter)):
        pos.append(-parameter[i][1] / (2 * parameter[i][0]))
    sorted_pos = sorted(enumerate(pos), key=lambda x: x[1])
    index = [i[0] for i in sorted_pos]
    order = [str(epc[num][7:9]) for num in index]
    return pos, order


def process(epc, time, phase):
    fit_epc, unfit_epc = [], []
    core_phase_list, core_time_list = [], []
    for i in range(0, len(epc)):
        flag, core_time, core_phase = core_v(time[i], phase[i])
        if flag == True:
            fit_epc.append(epc[i])
            core_time_list.append(core_time)
            core_phase_list.append(core_phase)
        else:
            unfit_epc.append(epc[i])
    return fit_epc, core_time_list, core_phase_list, unfit_epc


def main(epc=TEST_EPC):
    TEST_EPC = epc
    ori_epc, ori_time, ori_phase, __ = ObtainData(
        TEST_EPC, filename=TEST_FILE, antenna=TEST_ANTENNA)
    plot_epc, __, __, __ = ObtainData(
        PLOT_EPC, filename=TEST_FILE, antenna=TEST_ANTENNA)

    fit_epc, core_time, core_phase, unfit_epc = process(
        ori_epc, ori_time, ori_phase)

    fit_phase, parameter = get_fit(fit_epc, core_time, core_phase)

    pos, order = sort_epc(fit_epc, parameter)

    plot_order(epc, plot_epc, fit_epc, core_time, core_phase,
               fit_phase, ori_time, ori_phase, pos, order, parameter, unfit_epc, SHOW_FIG, SAVE_FIG)

    return order


if __name__ == '__main__':
    main()
