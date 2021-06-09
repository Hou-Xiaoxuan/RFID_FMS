#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2021/05/18
@Author  : xvrong
@File    : Core_V.py
@Function: PhaseFitting
'''
import matplotlib.colors as mcolors
import numpy as np
import math
import matplotlib.pyplot as plt
listen_epc = [
    "FFFF 0005 0000 0000 0000 0000",
    "FFFF 2006 0000 0000 0000 0000",
    "FFFF 2007 0000 0000 0000 0000",
]  # 实验中监控的标签列表
list_epc = []            # EPC列表
list_time = []           # Time列表
list_rssi = []           # RSSI列表
list_phase = []          # PHASE列表
first_time = 0           # 初始化一个开始时间，每次获得的开始时间不同


def process(old_time, old_data):
    "粘合数据范围"

    ct = 0
    jump = 4.5
    ct_list = [0]
    ct_loc = [0]
    for i in range(1, len(old_data)):
        if abs(old_data[i] - old_data[i - 1]) > jump:
            r = i + 1
            while r < len(old_data) and abs(old_data[r] - old_data[r - 1]) < jump:
                r += 1
            if r - i <= 3 and old_data[i] < 1:
                for index in range(i, r):
                    old_data[index] += 2 * math.pi

    for i in range(1, len(old_data)):
        if old_data[i] - old_data[i - 1] < -jump:
            ct += 1
            ct_list.append(ct)
            ct_loc.append(i)
        elif(old_data[i] - old_data[i - 1] > jump):
            ct -= 1
            ct_list.append(ct)
            ct_loc.append(i)
    ct_list.append(-20)
    ct_loc.append(len(old_data))
    l, r = 0, 0
    for i in range(1, len(ct_list)):
        if (ct_list[i] < ct_list[i - 1] and ct_loc[i] - ct_loc[i - 1] > 3):
            l = ct_loc[i - 1] + 1
            r = ct_loc[i] - 1
            break
    return old_time[l - 1: r - 1], old_data[l: r]


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
    plt.title("order is " + str([list_epc[num][7:9] for num in index]))
    for i in range(0, len(list_epc)):
        plt.plot(core_time[i], fit_phase[i],
                 color=mcolors.TABLEAU_COLORS[colors[i]], marker='.', linestyle=':')
        plt.scatter(core_time[i], core_phase[i],
                    color=mcolors.TABLEAU_COLORS[colors[i]], marker='*')
    # list.sort(list_epc)
    plt.legend([num[7:9] for num in list_epc], loc='best',
               bbox_to_anchor=(0.77, 0.2), fontsize='small')   # 设置图例
    plt.savefig('./Super_V.png', dpi=600)
    plt.show()
