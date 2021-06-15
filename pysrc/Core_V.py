#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2021/05/18
@Author  : xv_rong
@File    : Core_V.py
@Function: Core_V拟合，排序
'''
import matplotlib.colors as mcolors
import numpy as np
import math
import matplotlib.pyplot as plt
listen_epc = [
    "FFFF 2007 0000 0000 0000 0000",
    "FFFF 2006 0000 0000 0000 0000",
    "FFFF 0005 0000 0000 0000 0000",
    # "FFFF 0014 0000 0000 0000 0000",
    # "FFFF 0015 0000 0000 0000 0000",
    # "FFFF 0016 0000 0000 0000 0000",
    # "FFFF 0017 0000 0000 0000 0000",
    # "FFFF 0018 0000 0000 0000 0000",
    # "FFFF 0019 0000 0000 0000 0000",
    # "FFFF 0020 0000 0000 0000 0000",
    # "FFFF 0021 0000 0000 0000 0000",
    # "FFFF 0022 0000 0000 0000 0000",
    # "FFFF 0023 0000 0000 0000 0000",
    # "FFFF 0024 0000 0000 0000 0000",
    # "FFFF 0025 0000 0000 0000 0000",
    # "FFFF 0026 0000 0000 0000 0000",
    # "FFFF 0027 0000 0000 0000 0000",
    # "FFFF 0028 0000 0000 0000 0000",
    # "FFFF 0029 0000 0000 0000 0000",
]  # 实验中监控的标签列表
list_epc = []            # EPC列表
list_time = []           # Time列表
list_rssi = []           # RSSI列表
list_phase = []          # PHASE列表
first_time = 0           # 初始化一个开始时间，每次获得的开始时间不同


def process(old_time, tmp_data):
    "粘合数据范围"

    ct = 0
    jump = 3
    ct_list = []
    ct_loc = []
    # tmp_data = old_data.copy()
    tmp_data.insert(0, -math.inf)
    old_time.insert(0, 0)
    for i in range(1, len(tmp_data)):
        if abs(tmp_data[i] - tmp_data[i - 1]) > jump:
            r = i + 1
            while r < len(tmp_data) and abs(tmp_data[r] - tmp_data[r - 1]) < jump:
                r += 1
            if r - i <= 3 and tmp_data[i] < 1.28:
                for index in range(i, r):
                    tmp_data[index] += 2 * math.pi

            if r - i <= 3 and tmp_data[i] > 5:
                for index in range(i, r):
                    tmp_data[index] -= 2 * math.pi
    tmp_data.insert(len(tmp_data), math.inf)
    old_time.insert(len(old_time), math.inf)
    for i in range(1, len(tmp_data)):
        if tmp_data[i] - tmp_data[i - 1] < -jump:
            ct += 1
            ct_list.append(ct)
            ct_loc.append(i)
        elif(tmp_data[i] - tmp_data[i - 1] > jump):
            ct -= 1
            ct_list.append(ct)
            ct_loc.append(i)

    l, r = 0, 0
    for i in range(1, len(ct_list)):
        if (ct_list[i] < ct_list[i - 1]):
            l = ct_loc[i - 1]
            r = ct_loc[i]
            break
    return old_time[l: r], tmp_data[l: r]


def regression(time, phase):
    "多项式回归， 返回拟合后的数据"
    parameter = np.polyfit(time, phase, 2)
    func = np.poly1d(parameter)
    phase_fit = func(time)
    return phase_fit, -parameter[1] / (2 * parameter[0])


with open("./data.txt") as lines:
    """
    数据处理部分
    分割后的数据： Epc-Time-Rssi-Phase
    """

    for line in lines:
        tag_info = line.split('#')
        if len(tag_info) != 5:                   # 接收的TagInfo长度为4，分别为EPC, Time, Rssi, Phase，错误则开启下一个循环
            continue
        elif tag_info[0] not in listen_epc:
            continue
        else:
            if first_time == 0:                   # 第一次接收到Tag信息，将FirstTime初始化
                first_time = int(tag_info[1])
            if tag_info[0] not in list_epc:       # 若出现新标签，将新标签加入列表，为新标签创建各信息列表
                list_epc.append(tag_info[0])
                list_time.append([])
                list_rssi.append([])
                list_phase.append([])
            tag_index = list_epc.index(tag_info[0])        # 找出当前Tag所处列表位置

            # 将相应Tag信息入列表
            list_time[tag_index].append(
                (int(tag_info[1]) - first_time) / 1000000)        # 对时间处理为精度0.1s
            list_rssi[tag_index].append(float(tag_info[2]))
            list_phase[tag_index].append(float(tag_info[3]))

    """粘合数据"""

    pos = [0 for i in range(0, len(list_epc))]
    core_phase = [[] for i in range(0, len(list_epc))]
    core_time = [[] for i in range(0, len(list_epc))]
    fit_phase = [[] for i in range(0, len(list_epc))]
    for i in range(0, len(list_epc)):
        [core_time[i], core_phase[i]] = process(list_time[i], list_phase[i])
        [fit_phase[i], pos[i]] = regression(core_time[i], core_phase[i])
    colors = list(mcolors.TABLEAU_COLORS.keys())  # 颜色变化

    sorted_pos = sorted(enumerate(pos), key=lambda x: x[1])
    index = [i[0] for i in sorted_pos]
    pos = [i[1] for i in sorted_pos]
    plt.figure("order")
    print("order is " + str([list_epc[num][7:9] for num in index]))
    plt.title("order is " + str([list_epc[num][7:9] for num in index]))
    for i in range(0, len(list_epc)):
        plt.plot(core_time[i], fit_phase[i],
                 color=mcolors.TABLEAU_COLORS[colors[i]], marker='.', linestyle=':')

        plt.scatter(list_time[i], list_phase[i],
                    color=mcolors.TABLEAU_COLORS[colors[i + 1]], marker='*')

        plt.scatter(core_time[i], core_phase[i],
                    color=mcolors.TABLEAU_COLORS[colors[i]], marker='*')
    # list.sort(list_epc)
    plt.legend([num[7:9] for num in list_epc], loc='best',
               bbox_to_anchor=(0.77, 0.2), fontsize='small')   # 设置图例
    plt.savefig('./Super_V.png', dpi=600)
    plt.show()
