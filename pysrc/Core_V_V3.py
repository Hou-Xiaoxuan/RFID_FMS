#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2021/06/19
@Author  : xv_rong
@File    : Core_V.py
@Function: Core_V_V5拟合，排序
           1. 查找分割点，分割点在核心V区，且能将核心V区分割成两部分
           2. 进行两边向中间的逼近
           待用
           1. 补充空缺数据
           2. 特判分割点在左右两端
           3. ？处理核心V区特别小的情况，或者调整天线到一个适当的高度
           4. 找不到使用core_V.py方法

'''
import bisect
import matplotlib.colors as mcolors
import numpy as np
import math
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
listen_epc = [
    "FFFF 2006 0000 0000 0000 0000",
    # "FFFF 2007 0000 0000 0000 0000",
    # "FFFF 0005 0000 0000 0000 0000",
    # "FFFF 0011 0000 0000 0000 0000",
    # "FFFF 0012 0000 0000 0000 0000",
    # "FFFF 0013 0000 0000 0000 0000",
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
]  # 实验中欲监控的标签列表
list_epc = []            # 天线检测到的标签列表
list_time = []           # Time列表
list_rssi = []           # RSSI列表
list_phase = []          # PHASE列表
first_time = 0           # 初始化一个开始时间，每次获得的开始时间不同


def regression(time, phase):
    "多项式回归， 返回拟合后的数据"
    parameter = np.polyfit(time, phase, 2)
    func = np.poly1d(parameter)
    phase_fit = func(time)
    return phase_fit, parameter


def check_three(half_fit_data, orign_data):
    r2 = r2_score(orign_data, half_fit_data)
    # 0.97
    return r2 < 0.97


def cal_boundry_l(l, mid, old_time, old_data):
    flag = True
    while flag and mid - l >= 3:
        # 对[l,mid)的数据进行二次拟合
        [fit_phase, parameter] = regression(
            old_time[l:mid], old_data[l:mid])
        sym = -parameter[1] / (2 * parameter[0])   # 计算对称轴
        sym_index = bisect.bisect(old_time, sym)  # 拟合后的曲线中轴位置
        half_index = (l + mid) // 2
        # 若开口向上，或者中轴和左边界距离过近，无法进行下一次拟合，或者中轴超过右边界则认为范围选取不当
        if parameter[0] > 0 or sym_index - l < 3 or mid - sym_index < 3:
            l += 1
        else:
            # 对[l, half_index)位置进行拟合
            [l_fit_phase, l_parameter] = regression(
                old_time[l:half_index], old_data[l:half_index])
            # 对[half_index, r)位置进行拟合
            [r_fit_phase, r_parameter] = regression(
                old_time[half_index:mid], old_data[half_index:mid])
            # 若开口向上，则认为认为范围选取不当
            if l_parameter[0] > 0 or r_parameter[0] > 0:
                l += 1
            else:
                # 检验两次拟合的相似程度，如果相似程度低，则认为范围选取不当
                if check_three(l_fit_phase,  fit_phase[0:half_index - l]) and check_three(r_fit_phase, fit_phase[half_index - l: mid - l]):
                    l += 1
                else:
                    flag = False
    return l


def cal_boundry_r(r, mid, old_time, old_data):
    flag = True
    while flag and r - mid >= 3:
        # 对[mid,r)的数据进行二次拟合
        [fit_phase, parameter] = regression(
            old_time[mid:r], old_data[mid:r])
        sym = -parameter[1] / (2 * parameter[0])   # 计算对称轴
        sym_index = bisect.bisect(old_time, sym)  # 拟合后的曲线中轴位置
        half_index = (r + mid) // 2
        # 若开口向上，或者中轴和左边界距离过近，无法进行下一次拟合，或者中轴超过右边界则认为范围选取不当
        if parameter[0] > 0 or r - sym_index < 3 or sym_index - mid < 3:
            r -= 1
        else:
            # 对[mid, half_index)位置进行拟合
            [half_fit_phase_l, parameter_l] = regression(
                old_time[mid:half_index], old_data[mid:half_index])
            # 对[half_index, r)位置进行拟合
            [half_fit_phase_r, parameter_r] = regression(
                old_time[half_index:r], old_data[half_index:r])
            # 若开口向上，则认为认为范围选取不当
            if parameter_l[0] > 0 or parameter_r[0] > 0:
                r -= 1
            else:
                # 检验两次拟合的相似程度，如果相似程度低，则认为范围选取不当
                if check_three(half_fit_phase_l,  fit_phase[0: half_index - mid]) and check_three(half_fit_phase_r,  fit_phase[half_index - mid:r]):
                    r -= 1
                else:
                    flag = False
    return r


def process(old_time, old_data):
    '''
    寻找核心V区
    '''
    ct = 0        # 当前phass的去周期高度
    jump = 4      # 判断phass值是否发生跳跃的阈值
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

    # 寻找预备分割点
    mid_orign = []
    max_windows_size = 15
    min_windows_size = 10
    for i in range(len(old_data)):
        if (i - max_windows_size < 0 or i + max_windows_size > len(old_data)):
            continue

        level = bisect.bisect_right(ct_loc, i) - 1
        windows_l = max(i - max_windows_size, ct_loc[level])
        if i - windows_l <= min_windows_size:
            continue
        parameter_l = np.polyfit(
            old_time[windows_l: i], old_data[windows_l: i], 1)

        windows_r = min(i + max_windows_size, ct_loc[level + 1])
        if windows_r - i <= min_windows_size:
            continue
        parameter_r = np.polyfit(
            old_time[i: windows_r], old_data[i: windows_r], 1)

        if (parameter_l[0] > 0 and parameter_r[0] < 0):
            mid_orign.append(i)

    # 再次筛选
    # 标兵数据
    mid_orign.append(math.inf)
    before = 0
    l, r = [], []
    for i in range(1, len(mid_orign)):
        if (mid_orign[i] - mid_orign[i - 1] > 3):
            if i - before >= 4:
                level = bisect.bisect_right(ct_loc, mid_orign[before + 2]) - 1
                # min_windows_size保持一致
                l_tmp = cal_boundry_l(
                    ct_loc[level], mid_orign[i - 1] + min_windows_size, old_time, old_data)
                if mid_orign[i - 1] - l_tmp > 7:
                    r_tmp = cal_boundry_r(
                        ct_loc[level + 1], l_tmp, old_time, old_data)
                else:
                    r_tmp = cal_boundry_r(
                        ct_loc[level + 1], mid_orign[before] + min_windows_size, old_time, old_data)
                    l_tmp = cal_boundry_l(
                        ct_loc[level], r_tmp, old_time, old_data)

                l_tmp = cal_boundry_l(
                    ct_loc[level], r_tmp, old_time, old_data)
                if r_tmp - l_tmp >= 15:
                    l.append(l_tmp)
                    r.append(r_tmp)
            before = i

    max_r2, best_index = 0, 0
    for i in range(len(l)):
        [fit_data, parameter] = regression(
            old_time[l[i]:r[i]], old_data[l[i]:r[i]])
        sym = -parameter[1] / (2 * parameter[0])   # 计算对称轴
        half_index = bisect.bisect(old_time, sym)  # 拟合后的曲线中轴位置
        if parameter[0] > 0 or r[i] < half_index or half_index < l[i]:
            continue
        r2 = r2_score(old_data[l[i]:r[i]], fit_data)
        if (r2 > max_r2):
            max_r2 = r2
            best_index = i

    return old_time[l[best_index]: r[best_index]], old_data[l[best_index]: r[best_index]]


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
    parameter = [0 for i in range(0, len(list_epc))]
    core_phase = [[] for i in range(0, len(list_epc))]
    core_time = [[] for i in range(0, len(list_epc))]
    fit_phase = [[] for i in range(0, len(list_epc))]
    for i in range(0, len(list_epc)):
        [core_time[i], core_phase[i]] = process(list_time[i], list_phase[i])
        [fit_phase[i], parameter[i]] = regression(core_time[i], core_phase[i])
        pos[i] = -parameter[i][1] / (2 * parameter[i][0])
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
