'''
Author: xv_rong
Date: 2021-09-24 13:50:59
LastEditors: xv_rong
LastEditTime: 2021-09-24 21:45:47
Description: 
FilePath: /RFID_FMS/test.py
'''
from core_v import up_small_shake
from plot_result import plot_order
from core_v import core_v
from core_v import derivation
import numpy as np
from pysrc.ObtainData import ObtainData
import matplotlib.pyplot as plt
from core_v import find_N
from core_v import select_boundary
PLOT_EPC = '2d'
TEST_EPC = '2d'
TEST_ANTENNA = '1,9'
TEST_FILE = 'Data/2021-09-17/18-10-28.txt'
SHOW_FIG = True


def main():
    ori_epc, ori_time, ori_phase, __ = ObtainData(
        TEST_EPC, filename=TEST_FILE, antenna=TEST_ANTENNA)
    plot_epc, __, __, __ = ObtainData(
        PLOT_EPC, filename=TEST_FILE, antenna=TEST_ANTENNA)
    for i in range(len(ori_time)):
        plt.scatter(ori_time[i], ori_phase[i])
        plt.ylim(-6, 6)
        plt.title(ori_epc[i])
        up_small_shake(ori_phase[i])

        dot = 30
        k, b = derivation(ori_time[i], ori_phase[i], dot)
        time_one = ori_time[i][0 + dot: len(ori_time[i]) - dot]
        l, r = find_N(k, time_one)
        flag, l, r = select_boundary(k, time_one, l, r)
        if flag:
            plt.scatter(time_one, k)
            plt.scatter(time_one[l:r], k[l:r])
            plt.show()


if __name__ == '__main__':
    main()
