'''
Author: LinXuan
Date: 2021-09-26 19:35:16
Description: 使用拟合程序来粗略地得到数据集
LastEditors: LinXuan
LastEditTime: 2021-09-26 21:43:47
FilePath: /RFID_FMS/pysrc/CNN/CreatDataSet.py
'''
import bisect
import json

from CoreV2_0.main import get_fit, get_order, process, plot_order
from ManageData.ObtainData import ObtainData
PLOT_EPC = '2d-3b'
TEST_EPC = '2d-3b'
TEST_ANTENNA = '1,9'
TEST_FILE = '/Data/2021-09-17/18-26-44.txt'[1:]
SHOW_FIG = True
SAVE_FIG = True


def creat_data(ori_time, ori_phase, count_pos):
    temp_Y = [bisect.bisect_right(time, pos) for time, pos in zip(ori_time, count_pos)]
    # ori_time[Y]是大于pos的, 进行微调
    Y = [y if abs(time[y] - pos) < abs(time[y - 1] - pos) else y - 1 for time, y, pos in zip(ori_time, temp_Y, count_pos)]
    target_filename = "./Data/Dataset/" + TEST_FILE.split('/')[-1].replace(".txt", ".json")
    dic = dict()

    for i in range(len(Y)):
        dic[i] = dict({
            "time": ori_time[i],
            "phase": ori_phase[i],
            "y": Y[i]
        })
    with open(target_filename, "w") as f:
        json.dump(dic, f)


def main(epc=TEST_EPC):
    TEST_EPC = epc
    ori_epc, ori_time, ori_phase, __ = ObtainData(
        TEST_EPC, filename=TEST_FILE, antenna=TEST_ANTENNA)
    plot_epc, __, __, __ = ObtainData(
        PLOT_EPC, filename=TEST_FILE, antenna=TEST_ANTENNA)

    fit_epc, core_time, core_phase, unfit_epc = process(
        ori_epc, ori_time, ori_phase)

    fit_phase, parameter = get_fit(fit_epc, core_time, core_phase)

    pos, order = get_order(fit_epc, parameter)

    plot_order(epc, plot_epc, fit_epc, core_time, core_phase,
               fit_phase, ori_time, ori_phase, pos, order, parameter, unfit_epc)

    # form here
    creat_data(ori_time, ori_phase, pos)


if __name__ == '__main__':
    # ori = "2c"
    # while(int(ori, 16) <= int("3b", 16)):
    #     ori = str(hex(int(ori, 16) + 1))
    #     main(ori)
    main()
