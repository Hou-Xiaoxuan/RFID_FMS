#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File         : Core_V_V2.py
@Date         : 2021/06/27 09:06:18
@Author       : xv_rong
@version      : 1.0
@Function     : Core_V_V2拟合，排序，分模块
                1. 查找核心V区峰值
                2. 两边向中间的逼近
                3. 上升小核心V
@TODO         : 0. 改进上升核心V区逻辑
                1. 改善选择核心V区的逻辑
                2. 根据历史a值判断拟合是否成功
                3. 找不到时使用其他方法
                4. 特判分割点在左右两端
                5. 多个结果返回一个更合理的结果
                6. 将标签列表，读取数据和画图逻辑分割出去
'''

import bisect
# from jedi.inference.context import FunctionContext
import matplotlib.colors as mcolors
import numpy as np
import math
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import mean
from numpy.lib.function_base import average
from sklearn.metrics import r2_score
listen_epc = [
    # "0000 000F 2000 0000 0000 0000",
    # "0000 0010 2000 0000 0000 0000",
    # "0000 0011 2000 0000 0000 0000",
    # "0000 0012 2000 0000 0000 0000",
    # "0000 0013 2000 0000 0000 0000",
    "0000 0014 2000 0000 0000 0000",
    # "0000 0015 2000 0000 0000 0000",
    # "0000 0016 2000 0000 0000 0000",
    # "0000 0017 2000 0000 0000 0000",
    # "0000 0018 2000 0000 0000 0000",
    # "0000 0019 2000 0000 0000 0000",
    # "0000 001A 2000 0000 0000 0000",
    # "0000 001B 2000 0000 0000 0000",
    # "0000 001C 2000 0000 0000 0000",
    # "0000 001D 2000 0000 0000 0000",
    # "0000 0009 0000 0000 0000 0000",
    # "0000 000A 0000 0000 0000 0000",
    # "0000 000B 0000 0000 0000 0000",
    # "0000 000C 0000 0000 0000 0000",
    # "0000 000D 0000 0000 0000 0000",
    # "0000 000E 0000 0000 0000 0000",
]  # 实验中欲监控的标签列表
list_epc = []            # 天线检测到的标签列表
list_time = []           # Time列表
list_rssi = []           # RSSI列表
list_phase = []          # PHASE列表
first_time = 0           # 初始化一个开始时间，每次获得的开始时间不同


def regression(time, data):
    '''
    @Description
    -------
    处理在0和2PI附近不稳定的值，防止出现错误的跳跃

    @Parameters
    -------
    time       :  时间
    data       :  phase

    @Returns
    -------
    phase_fit  :  拟合后的phase
    parameter  ： 拟合参数

    @Warns
    -------
    NONE

    '''
    parameter = np.polyfit(time, data, 2)
    func = np.poly1d(parameter)
    phase_fit = func(time)
    return phase_fit, parameter


def check(fit_data, orign_data):
    '''
    @Description
    ---------
    检查拟合的phase和原始phase的契合程度

    @Parameters
    -------
    fit_data    :  拟合值
    orign_data  :  原始值

    @Returns
    -------
    拟合度高 True 拟合度低 False

    @Warns
    -------
    NONE

    '''
    r2 = r2_score(orign_data, fit_data)
    return r2 >= 0.8  # 程序运行的关键参数


def preprocess_data(time, data):
    '''
    @Description
    ---------
    预处理数据，主要是两端插入标兵数据

    @Parameters
    -------
    time      :  时间
    data      :  phase

    @Returns
    -------
    time      :  处理后时间
    data      :  处理后phase

    @Warns
    -------
    NONE

    '''

    # time = time.copy()
    # data = data.copy()
    # 哨兵数据，防止数据不出现从小到大的跳跃
    data.insert(len(data), math.inf)
    time.insert(len(time), math.inf)
    # 哨兵数据，防止第一个数据被舍弃，或不能处理
    data.insert(0, math.inf)
    time.insert(0, 0)
    return time, data


def up_small_shake(data, too_small=5, jump=4, near_PI=1.28):
    '''
    @Description
    ---------
    将0和2PI附近发生跳跃的值和周围的翼合并

    @Parameters
    -------
    data      :  phase
    too_small :  一个震动数据量的临界值
    jump      :  发生跳跃的临界值
    near_PI   :  判断距离两个边界距离的的临界值

    @Returns
    -------
    data      :  处理后的数据

    @Warns
    -------
    NONE

    '''
    # data = data.copy()
    for i in range(1, len(data)):
        if abs(data[i] - data[i - 1]) > jump:  # i-1到i处出现跳跃
            # 检测从i到下一次跳跃的数据量
            r = i + 1
            while r < len(data) and abs(data[r] - data[r - 1]) < jump:
                r += 1

            # 数据量小于等于too_small，并且值处在0附近，将数据上升
            if r - i <= too_small and data[i] < near_PI:
                for index in range(i, r):
                    data[index] += 2 * math.pi
            # 数据量小于等于too_small，并且值处在2PI附近，将数据下降
            elif r - i <= too_small and data[i] > 2 * math.pi - near_PI:
                for index in range(i, r):
                    data[index] -= 2 * math.pi
    return data


def splite_data(data, jump=2):
    '''
    @Description
    ---------
    根据jump值分割数据

    @Parameters
    -------
    data       :  phase
    jump       :  发生跳跃的临界值

    @Returns
    -------
    ct_loc     :  发生跳跃的位置

    @Warns
    -------
    NONE

    '''
    ct_loc = []   # 发生跳跃的位置，左闭右开

    for i in range(1, len(data)):
        if data[i] - data[i - 1] < -jump:
            # ct += 1
            # ct_list.append(ct)
            ct_loc.append(i)
        elif(data[i] - data[i - 1] > jump):
            # ct -= 1
            # ct_list.append(ct)
            ct_loc.append(i)
    return ct_loc


def up_small_block(data, ct_loc, small_V_size=15, near_PI=1.28):
    '''
    @Description
    ---------
    将数据量很小的块，上升2PI

    @Parameters
    -------
    data          :  phase
    ct_loc        :  发生跳跃的位置
    small_V_size  :  程序默认能辨认的最小V区大小，数据量小于这个大小的块，需要上升
    near_PI       :  判断距离两个边界距离的的临界值

    @Returns
    -------
    data          :  phase
    ct_loc        :  发生跳跃的位置，将小区域和两边合并

    @Warns
    -------
    需要改进
    可能出现问题，一个小V区和两侧的距离可能不是2PI,而且可能不是处于一个接近0的位置

    '''
    # data = data.copy()
    # ct_loc = ct_loc.copy()
    i = 1
    while i < len(ct_loc) - 1:
        if ct_loc[i] - ct_loc[i - 1] < small_V_size:
            # 两端的限制
            if data[ct_loc[i - 1] - 1] > 2 * math.pi - near_PI and data[ct_loc[i]] > 2 * math.pi - near_PI:
                for index in range(ct_loc[i - 1], ct_loc[i]):
                    data[index] += 2 * math.pi
                ct_loc.pop(i - 1)
                ct_loc.pop(i - 1)
            else:
                i = i + 1
        else:
            i = i + 1
    return data, ct_loc


def find_peek_V(time, data, ct_loc, window_size=7):
    '''
    @Description
    ---------
    寻找所有可能的V区顶点，可能寻找到错误的

    @Parameters
    -------
    data       :  phase

    @Returns
    -------
    peek       :  V区顶点

    @Warns
    -------
    可能寻找到错误的

    '''
    peek = []  # 可能的V区顶点列表
    stack = []  # 单调栈
    lnum = [0 for __ in range(len(data))]  # 一个数据左侧连续小于其的数据数量
    rnum = [0 for __ in range(len(data))]  # 一个数据右侧连续小于其的数据数量
    # ct_loc = splite_data(data, jump=2)   # 分割数据，分割条件更苛刻
    # 单调栈，一个 >= ,另一个 > 避免双峰
    for i in range(0, len(data)):
        if i in ct_loc:
            while stack:
                j = stack.pop()
                lnum[j] = i - j - 1
        # >
        while stack and data[i] > data[stack[-1]]:
            j = stack.pop()
            lnum[j] = i - j - 1
        stack.append(i)

    stack.clear()
    for i in range(len(data) - 1, -1, -1):
        if i + 1 in ct_loc:
            while stack:
                j = stack.pop()
                rnum[j] = j - i - 1
        # >=
        while stack and data[i] >= data[stack[-1]]:
            j = stack.pop()
            rnum[j] = j - i - 1
        stack.append(i)

    for i in range(len(data)):
        if (lnum[i] >= window_size and rnum[i] >= window_size):
            parameter = np.polyfit(
                time[i - window_size:i + window_size + 1], data[i - window_size: i + window_size + 1], 2)
            if parameter[0] <= -0.05:
                peek.append(i)
    return peek


def find_boundary(time, data, ct_loc, peek, small_V_size=15):
    '''
    @Description
    ---------
    寻找边界

    @Parameters
    -------
    data          :  phase
    time          :  时间
    ct_loc        :  发生跳跃的位置
    peek          :  V区顶点
    small_V_size  :  程序默认能辨认的最小V区大小，数据量小于这个大小的块，则认为不是一个正确拟合

    @Returns
    -------
    l_list        :  V区的左边界列表
    r_list        :  V区的右边界列表

    @Warns
    -------
    左右边界是一个列表，后续需要选择的一个

    '''
    window_size = small_V_size // 2
    l_list, r_list = [], []
    for i in range(len(peek)):
        level = bisect.bisect_right(ct_loc, peek[i]) - 1
        # peek[i] + window_size为v区顶点可以确定的右边界
        l_tmp = cal_boundry_l(
            ct_loc[level], min(peek[i] + window_size, len(data) - 1), time, data)
        if peek[i] - l_tmp >= 5:
            # 根据找到的左边界，压缩右边的边界
            r_tmp = cal_boundry_r(
                ct_loc[level + 1], l_tmp, time, data)
            # 重新压缩左边界
            l_tmp = cal_boundry_l(
                ct_loc[level], r_tmp, time, data)
        # 若左边界效果不好
        else:
            # peek[i] + window_size为v区顶点可以确定的左边界
            r_tmp = cal_boundry_r(
                ct_loc[level + 1], max(1, peek[i] - window_size), time, data)
            # 根据找到的右边界，压缩左边的边界
            l_tmp = cal_boundry_l(
                ct_loc[level], r_tmp, time, data)
            # 重新压缩右边界
            r_tmp = cal_boundry_r(
                ct_loc[level + 1], l_tmp, time, data)
        # 验证数据量符合要求
        if r_tmp - l_tmp >= small_V_size:
            l_list.append(l_tmp)
            r_list.append(r_tmp)
    return l_list, r_list


def cal_boundry_l(l, r, time, data):
    '''
    @Description
    ---------
    固定右边界，寻找左边界

    @Parameters
    -------
    l          :  左边界起始点
    r          :  固定右边界
    time       :  时间
    data       :  phase

    @Returns
    -------
    l          :  确定的左边界

    @Warns
    -------
    l需要在核心v区外或者边界处
    r需要在核心v区内偏右侧

    '''
    flag = True
    while flag and r - l >= 3:

        [fit_phase, parameter] = regression(
            time[l:r], data[l:r])  # 对[l,r)的数据进行二次拟合
        sym = -parameter[1] / (2 * parameter[0])   # 计算对称轴
        sym_index = bisect.bisect(time, sym)  # 拟合后的曲线中轴位置
        half_index = (l + r) // 2
        # 若开口向上，或者中轴和左边界距离过近，无法进行下一次拟合，或者中轴超过右边界则认为范围选取不当
        if parameter[0] > 0 or sym_index - l < 3 or r - sym_index < 3:
            l += 1
        else:
            # 对[l, half_index)位置进行拟合
            [l_fit_phase, l_parameter] = regression(
                time[l:half_index], data[l:half_index])
            # 对[half_index, r)位置进行拟合
            [r_fit_phase, r_parameter] = regression(
                time[half_index:r], data[half_index:r])
            # 若开口向上，则认为认为范围选取不当
            if l_parameter[0] > 0 or r_parameter[0] > 0:
                l += 1
            else:
                # 这个逻辑可能会过严
                # 检验两次拟合左侧的相似程度，如果相似程度低，则认为范围选取不当
                if check(l_fit_phase, fit_phase[0:half_index - l]) and check(r_fit_phase, fit_phase[half_index - l: r - l]):
                    flag = False
                else:
                    l += 1
    return l


def cal_boundry_r(r, l, time, data):
    '''
    @Description
    ---------
    固定左边界，寻找右边界

    @Parameters
    -------
    l          :  固定左边界
    r          :  右边界起始点
    time       :  时间
    data       :  phase

    @Returns
    -------
    r          :  确定的左边界

    @Warns
    -------
    l需要在核心v区内偏左侧
    r需要在核心v区外或者边界处

    '''
    flag = True
    while flag and r - l >= 3:
        # 对[l,r)的数据进行二次拟合
        [fit_phase, parameter] = regression(
            time[l:r], data[l:r])
        sym = -parameter[1] / (2 * parameter[0])   # 计算对称轴
        sym_index = bisect.bisect(time, sym)  # 拟合后的曲线中轴位置
        half_index = (r + l) // 2
        # 若开口向上，或者中轴和左边界距离过近，无法进行下一次拟合，或者中轴超过右边界则认为范围选取不当
        if parameter[0] > 0 or r - sym_index < 3 or sym_index - l < 3:
            r -= 1
        else:
            # 对[l, half_index)位置进行拟合
            [l_fit_phase, parameter_l] = regression(
                time[l:half_index], data[l:half_index])
            # 对[half_index, r)位置进行拟合
            [r_fit_phase, parameter_r] = regression(
                time[half_index:r], data[half_index:r])
            # 若开口向上，则认为认为范围选取不当
            if parameter_l[0] > 0 or parameter_r[0] > 0:
                r -= 1
            else:
                # 检验拟合右侧的相似程度，如果相似程度低，则认为范围选取不当
                # 这个逻辑可能会过严
                if check(r_fit_phase, fit_phase[half_index - l:r - l]) and check(l_fit_phase, fit_phase[0: half_index - l]):
                    flag = False
                else:
                    r -= 1
    return r


def select_result(time, data, l_list, r_list):
    '''
    @Description
    ---------
    从获得的v区边界中选择一个

    @Parameters
    -------
    time            :  时间
    data            :  数据
    l_list          :  左边界列表
    r_list          :  右边界列表

    @Returns
    -------
    l               :  左边界
    r               :  右边界

    @Warns
    -------
    选择一个r2最大的，不一定能选择出对的

    '''
    #
    max_r2, best_index = -math.inf, -1
    for i in range(len(l_list)):
        [fit_data, parameter] = regression(
            time[l_list[i]:r_list[i]], data[l_list[i]:r_list[i]])
        sym = -parameter[1] / (2 * parameter[0])   # 计算对称轴
        sym_index = bisect.bisect(time, sym)  # 拟合后的曲线中轴位置
        # 需要开口向下，中轴在边界之间
        if parameter[0] > 0 or r_list[i] < sym_index or sym_index <= l_list[i]:
            continue
        r2 = r2_score(data[l_list[i]:r_list[i]], fit_data)
        if (r2 > max_r2):
            max_r2 = r2
            best_index = i
    if best_index == -1:
        return -1, -1
    return l_list[best_index], r_list[best_index]


def process(time, data):
    '''
    @Description
    ---------
    寻找核心V区

    @Parameters
    -------
    time        :  时间
    data        :  phass

    @Returns
    -------
    l           :  左边界
    r           :  右边界

    @Warns
    -------
    NONE

    '''

    # 处理在0和6附近不稳定的值，防止出现错误的跳跃
    near_PI = 1.28  # 判断数据接近0或2PI的阈值
    too_small = 5   # 判断数据量是否太小的阈值
    jump = math.pi        # 判断phase是否发生跳跃的阈值
    small_V_size = 15  # 能处理的最小core_V区大小
    window_size = small_V_size // 2  # 根据small_V_size确定的一般V区大小
    # 预处理
    time, data = preprocess_data(time, data)
    # 处理振动数据
    data = up_small_shake(
        data, too_small, jump, near_PI)
    # 分割数据
    ct_loc = splite_data(data, jump)
    # 处理小块数据
    data, ct_loc = up_small_block(
        data, ct_loc, small_V_size, near_PI)
    # 寻找V区顶点
    peek = find_peek_V(
        time, data, ct_loc, window_size)
    # 寻找左右边界
    l_list, r_list = find_boundary(time, data, ct_loc, peek,
                                   small_V_size)
    # 选择最佳边界
    l, r = select_result(time, data, l_list, r_list)
    return l, r


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
    ori_pos = []
    parameter = []
    core_phase = []
    core_time = []
    fit_phase = []
    fit_epc = []
    unfit_epc = []
    for i in range(0, len(list_epc)):
        l, r = process(list_time[i], list_phase[i])
        if l != -1 and r != -1:
            fit_epc.append(list_epc[i])
            core_time.append(list_time[i][l:r])
            core_phase.append(list_phase[i][l:r])
            [tmp_fit_phase, tmp_parameter] = regression(
                core_time[-1], core_phase[-1])
            fit_phase.append(tmp_fit_phase)
            parameter.append(tmp_parameter)
            ori_pos.append(-parameter[-1][1] / (2 * parameter[-1][0]))
        else:
            unfit_epc.append(list_epc[i])
    colors = list(mcolors.TABLEAU_COLORS.keys())  # 颜色变化
    len_colors = len(mcolors.TABLEAU_COLORS)  # 颜色长度
    # 排序
    sorted_pos = sorted(enumerate(ori_pos), key=lambda x: x[1])
    index = [i[0] for i in sorted_pos]
    pos = [i[1] for i in sorted_pos]
    # 画图
    plt.figure("order")
    plt.title("order is " + str([fit_epc[num][7:9] for num in index]) + " unfit:" +
              str([unfit_epc[num][7:9] for num in range(0, len(unfit_epc))]))

    for i in range(0, len(fit_epc)):
        plt.plot(core_time[i], fit_phase[i],
                 color=mcolors.TABLEAU_COLORS[colors[i % len_colors]], marker='.', linestyle=':')

        plt.scatter(list_time[i], list_phase[i],
                    color=mcolors.TABLEAU_COLORS[colors[i % len_colors]], marker='*')

        plt.scatter(core_time[i], core_phase[i],
                    color=mcolors.TABLEAU_COLORS[colors[i % len_colors]], marker='*')
    plt.legend([str(fit_epc[i][7:9]) + ' a:' + str(parameter[i][0]) for i in range(len(fit_epc))],
               loc='upper right', fontsize='small')   # 设置图例
    for i in range(0, len(fit_epc)):
        plt.plot([ori_pos[i]] * 20, [i / 10 for i in range(0, 60, 3)],
                 color=mcolors.TABLEAU_COLORS[colors[i % len_colors]])
    print(average(parameter, 0))
    plt.savefig('./Core_V.png', dpi=600)
    plt.show()
