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
    "FFFF 0011 0000 0000 0000 0000",
    "FFFF 0012 0000 0000 0000 0000",
    "FFFF 0013 0000 0000 0000 0000",
    "FFFF 0014 0000 0000 0000 0000",
    "FFFF 0015 0000 0000 0000 0000",
    "FFFF 0016 0000 0000 0000 0000",
    "FFFF 0017 0000 0000 0000 0000",
    "FFFF 0018 0000 0000 0000 0000",
    "FFFF 0019 0000 0000 0000 0000",
    "FFFF 0020 0000 0000 0000 0000",
    "FFFF 0021 0000 0000 0000 0000",
    "FFFF 0022 0000 0000 0000 0000",
    "FFFF 0023 0000 0000 0000 0000",
    "FFFF 0024 0000 0000 0000 0000",
    "FFFF 0025 0000 0000 0000 0000",
    "FFFF 0026 0000 0000 0000 0000",
    "FFFF 0027 0000 0000 0000 0000",
    "FFFF 0028 0000 0000 0000 0000",
    "FFFF 0029 0000 0000 0000 0000",
]  # 实验中欲监控的标签列表
list_epc = []            # 天线检测到的标签列表
list_time = []           # Time列表
list_rssi = []           # RSSI列表
list_phase = []          # PHASE列表
first_time = 0           # 初始化一个开始时间，每次获得的开始时间不同


def process(old_time, old_data):
    '''
    寻找核心V区
    '''
    ct = 0        # 当前phass的去周期高度
    jump = 3      # 判断phass值是否发生跳跃的阈值
    ct_list = []  # phass的去周期高度列表
    ct_loc = []   # 发生跳跃的位置，左闭右开

    # 不修改源数据，否则在处理不稳定值时改变源数据
    old_data = old_data.copy()
    old_time = old_time.copy()

    # 哨兵数据，防止数据不出现从小到大的跳跃
    old_data.insert(len(old_data), math.inf)
    old_time.insert(len(old_time), math.inf)
    # 哨兵数据，防止第一个数据被舍弃，或不能处理
    old_data.insert(0, math.inf)
    old_time.insert(0, 0)

    # 处理在0和6附近不稳定的值，防止出现错误的跳跃
    near_PI = 1.28  # 判断数据接近0或2PI的阈值
    too_small = 3   # 判断数据量是否太小的阈值
    for i in range(1, len(old_data)):
        if abs(old_data[i] - old_data[i - 1]) > jump:  # i-1到i处出现跳跃
            # 检测从i到下一次跳跃的数据量
            r = i + 1
            while r < len(old_data) and abs(old_data[r] - old_data[r - 1]) < jump:
                r += 1

            # 数据量小于等于too_small，并且值处在0附近，将数据上升
            if r - i <= too_small and old_data[i] < near_PI:
                for index in range(i, r):
                    old_data[index] += 2 * math.pi
            # 数据量小于等于too_small，并且值处在2PI附近，将数据下降
            elif r - i <= too_small and old_data[i] > math.pi - near_PI:
                for index in range(i, r):
                    old_data[index] -= 2 * math.pi

    # 根据跳跃分割数据
    for i in range(1, len(old_data)):
        if old_data[i] - old_data[i - 1] < -jump:
            ct += 1
            ct_list.append(ct)
            ct_loc.append(i)
        elif(old_data[i] - old_data[i - 1] > jump):
            ct -= 1
            ct_list.append(ct)
            ct_loc.append(i)

    # 寻找核心区
    l, r = 0, 0
    for i in range(1, len(ct_list)):
        # 核心区为第一个向上跳跃以前，且数据量不能小于10
        if (ct_list[i] < ct_list[i - 1] and ct_loc[i] - ct_loc[i - 1] >= 10):
            l = ct_loc[i - 1]
            r = ct_loc[i]
            break
    return old_time[l: r], old_data[l: r]


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
    len_colors = len(mcolors.TABLEAU_COLORS)  # 颜色长度
    sorted_pos = sorted(enumerate(pos), key=lambda x: x[1])
    index = [i[0] for i in sorted_pos]
    pos = [i[1] for i in sorted_pos]
    plt.figure("order")
    print("order is " + str([list_epc[num][7:9] for num in index]))
    plt.title("order is " + str([list_epc[num][7:9] for num in index]))

    for i in range(0, len(list_epc)):
        plt.plot(core_time[i], fit_phase[i],
                 color=mcolors.TABLEAU_COLORS[colors[i % len_colors]], marker='.', linestyle=':')

        plt.scatter(list_time[i], list_phase[i],
                    color=mcolors.TABLEAU_COLORS[colors[i % len_colors]], marker='*')

        plt.scatter(core_time[i], core_phase[i],
                    color=mcolors.TABLEAU_COLORS[colors[i % len_colors]], marker='*')
    # list.sort(list_epc)
    plt.legend([num[7:9] for num in list_epc],
               loc='upper right', fontsize='small')   # 设置图例
    plt.savefig('./Super_V.png', dpi=600)
    plt.show()
