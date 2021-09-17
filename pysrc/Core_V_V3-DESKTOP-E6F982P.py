#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File         : Core_V_V2.py
@Date         : 2021/06/27 09:06:18
@Author       : xv_rong
@version      : 1.0
@Function     : Core_V_V2拟合，排序，分模块
version3
'''

import bisect
from ObtainData import GenerateListenEpc
from DisplayData import DisplayData
from ObtainData import ObtainData
import matplotlib.colors as mcolors
import numpy as np
import math
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import mean, std
from numpy.lib.function_base import average
from sklearn.metrics import r2_score

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


def check(fit_data, orign_data, r2):
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
    return r2_score(orign_data, fit_data) >= r2  # 程序运行的关键参数


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


def splite_data(data, jump=math.pi - 0.5):
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
    i = 1
    while i < len(ct_loc) - 1:
        if ct_loc[i] - ct_loc[i - 1] <= small_V_size:
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
    while True:
        for i in range(len(data)):
            if (lnum[i] >= window_size and rnum[i] >= window_size):
                l = max(i - window_size, 1)
                r = min(i + window_size + 1, len(data) - 1)
                parameter = np.polyfit(
                    time[l:r], data[l:r], 2)
                if parameter[0] <= -0.05:
                    peek.append(i)
        if len(peek) > 0:
            break
        window_size -= 1
    return peek, window_size


def cal_boundry_l(l, r, time, data, r2):
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
            # 对[half_index, r)位置进行拟合
            [r_fit_phase, r_parameter] = regression(
                time[half_index:r], data[half_index:r])
            [l_fit_phase, l_parameter] = regression(
                time[l:half_index], data[l:half_index])
            # 这个逻辑可能会过严
            if check(r_fit_phase, fit_phase[half_index - l:r - l], r2) and r_parameter[0] < 0 and check(l_fit_phase, fit_phase[0: half_index - l], r2) and l_parameter[0] < 0:
                flag = False
            else:
                l += 1
    return l


def cal_boundry_r(r, l, time, data, r2):
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
            # 对[half_index, r)位置进行拟合
            [r_fit_phase, r_parameter] = regression(
                time[half_index:r], data[half_index:r])
            [l_fit_phase, l_parameter] = regression(
                time[l:half_index], data[l:half_index])
            # 这个逻辑可能会过严
            if check(r_fit_phase, fit_phase[half_index - l:r - l], r2) and r_parameter[0] < 0 and check(l_fit_phase, fit_phase[0: half_index - l], r2) and l_parameter[0] < 0:
                flag = False
            else:
                r -= 1
    return r


def find_boundary(time, data, ct_loc, signal_peek, window_size=7, r2=0):
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

    level = bisect.bisect_right(ct_loc, signal_peek) - 1
    # peek[i] + window_size为v区顶点可以确定的右边界
    l = cal_boundry_l(
        ct_loc[level], min(signal_peek + window_size, len(data) - 1), time, data, r2)
    if signal_peek + window_size - l >= 5:
        # 根据找到的左边界，压缩右边的边界
        r = cal_boundry_r(
            ct_loc[level + 1], l, time, data, r2)
        # 重新压缩左边界
        l = cal_boundry_l(
            ct_loc[level], r, time, data, r2)
    # 若左边界效果不好
    else:
        # peek[i] + window_size为v区顶点可以确定的左边界
        r = cal_boundry_r(
            ct_loc[level + 1], max(1, signal_peek - window_size), time, data, r2)
        # 根据找到的右边界，压缩左边的边界
        l = cal_boundry_l(
            ct_loc[level], r, time, data, r2)
        # 重新压缩右边界
        r = cal_boundry_r(
            ct_loc[level + 1], l, time, data, r2)
    return l, r


def binary_find_boundary(time, data, ct_loc, peek, min_V_size=15, window_size=7):
    l_list, r_list = [], []
    dim_l_list, dim_r_list = [], []
    for i in range(len(peek)):
        l_r2_init, r_r2_init = -1.0, 1.01
        l_r2, r_r2 = l_r2_init, r_r2_init
        while r_r2 - l_r2 > 0.01:
            r2 = (l_r2 + r_r2) / 2
            l, r = find_boundary(time, data, ct_loc, peek[i], window_size, r2)
            if r - l >= min_V_size:
                if (l_r2 == l_r2_init):
                    dim_l_list.append(l)
                    dim_r_list.append(r)
                l_r2 = r2
            else:
                r_r2 = r2
        if l_r2 != l_r2_init:
            l, r = find_boundary(time, data, ct_loc,
                                 peek[i], window_size, l_r2)
            l_list.append(l)
            r_list.append(r)
    return l_list, r_list, dim_l_list, dim_r_list


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
    return best_index


def find_Core_V(time, data, ct_loc, peek, min_V_size, window_size):
    best_index = -1
    l_list, r_list, dim_l_list, dim_r_list = binary_find_boundary(
        time, data, ct_loc, peek, min_V_size, window_size)
    best_index = select_result(time, data, l_list, r_list)
    if best_index == -1:
        return -1, -1, -1, -1
    return l_list[best_index], r_list[best_index], dim_l_list[best_index], dim_r_list[best_index]


def Core_V(time, data):
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
    jump = math.pi - 0.5        # 判断phase是否发生跳跃的阈值
    # 根据small_V_size确定的一般V区大小
    min_V_size = 15
    window_size = min_V_size // 2
    # 预处理
    time, data = preprocess_data(time, data)
    # 处理振动数据
    data = up_small_shake(
        data, too_small, jump, near_PI)
    # 分割数据
    ct_loc = splite_data(data, jump)
    # 处理小块数据
    data, ct_loc = up_small_block(data, ct_loc, min_V_size, near_PI)
    # 寻找V区顶点
    peek, window_size = find_peek_V(
        time, data, ct_loc, window_size)
    min_V_size = min(2 * window_size + 1, min_V_size)
    # 寻找核心V区
    l, r, dim_l, dim_r = find_Core_V(time, data, ct_loc, peek,
                                     min_V_size, window_size)
    return l, r, dim_l, dim_r


def process(list_epc, list_time, list_phase):
    dim_l_list, dim_r_list = [], []
    l_list, r_list = [], []
    fit_epc = []
    unfit_epc = []
    core_phase = []
    core_time = []
    for i in range(0, len(list_epc)):
        l, r, dim_l, dim_r = Core_V(list_time[i], list_phase[i])
        if l != -1 and r != -1:
            fit_epc.append(list_epc[i])
            core_time.append(list_time[i][l:r])
            core_phase.append(list_phase[i][l:r])
            l_list.append(l)
            r_list.append(r)
            dim_l_list.append(dim_l)
            dim_r_list.append(dim_r)
        else:
            unfit_epc.append(list_epc[i])
    return fit_epc, core_time, core_phase, l_list, r_list, dim_l_list, dim_r_list, unfit_epc


def get_fit(fit_epc, core_time, core_phase):
    fit_phase = []
    parameter = []
    ori_pos = []
    for i in range(len(fit_epc)):
        [tmp_fit_phase, tmp_parameter] = regression(
            core_time[i], core_phase[i])
        fit_phase.append(tmp_fit_phase)
        parameter.append(tmp_parameter)
        ori_pos.append(-tmp_parameter[1] / (2 * tmp_parameter[0]))
    return fit_phase, parameter


def get_order(fit_epc, parameter):
    pos = []
    for i in range(len(parameter)):
        pos.append(-parameter[i][1] / (2 * parameter[i][0]))
    sorted_pos = sorted(enumerate(pos), key=lambda x: x[1])
    index = [i[0] for i in sorted_pos]
    order = [str(fit_epc[num][7:9]) for num in index]
    return pos, order


def get_plot(figname, plot_epc, fit_epc, core_time, core_phase, fit_phase, list_time, list_phase, pos, order, parameter, unfit_epc):
    colors = list(mcolors.TABLEAU_COLORS.keys())  # 颜色变化
    len_colors = len(mcolors.TABLEAU_COLORS)  # 颜色长度
    plt.figure(figname, figsize=(16, 9))
    plt.title("order is " + str(order) + " unfit:" +
              str([unfit_epc[num][7:9] for num in range(0, len(unfit_epc))]))

    for i in range(len(fit_epc)):
        if (fit_epc[i] in plot_epc):
            plt.plot(core_time[i], fit_phase[i],
                     color=mcolors.TABLEAU_COLORS[colors[i % len_colors]], marker='.', linestyle=':')

            plt.scatter(list_time[i], list_phase[i],
                        color=mcolors.TABLEAU_COLORS[colors[i % len_colors]], marker='*')

            plt.scatter(core_time[i], core_phase[i],
                        color=mcolors.TABLEAU_COLORS[colors[i % len_colors]], marker='*')
    plt.legend([str(plot_epc[i][7:9]) + ' a:' + str(round(parameter[i][0], 2)) for i in range(len(plot_epc))],
               loc='upper right', fontsize='small')   # 设置图例
    for i in range(len(fit_epc)):
        if (fit_epc[i] in plot_epc):
            plt.plot([pos[i]] * 20, [i / 10 for i in range(0, 60, 3)],
                     color=mcolors.TABLEAU_COLORS[colors[i % len_colors]])

    plt.savefig(figname + '.png')


def get_shape_boundary(time, data, l, r, dim_l, dim_r, mu):
    best_l, best_r = l, r
    best_mu = math.inf
    for i in range(dim_l, l + 1):
        for j in range(r, dim_r + 1):
            [__, parameter] = regression(time[i:j], data[i:j])
            if abs(best_mu - mu) > abs(parameter[0] - mu):
                best_l = i
                best_r = j
                best_mu = parameter[0]
    return best_l, best_r


def adapt_shape(fit_epc, list_time, list_phase, l_list, r_list, dim_l_list, dim_r_list, parameter):
    a_list = [parameter[i][0] for i in range(len(parameter))]
    mu = average(a_list)
    theta = std(a_list)
    tmp_a_list = []
    for a in a_list:
        if a > mu - theta and a < mu + theta:
            tmp_a_list.append(a)
    mu = average(tmp_a_list)
    theta = std(tmp_a_list)
    core_time, core_phase = [], []
    for i in range(len(a_list)):
        l, r = get_shape_boundary(
            list_time[i], list_phase[i], l_list[i], r_list[i], dim_l_list[i], dim_r_list[i], mu)
        l_list[i] = l
        r_list[i] = r
    for i in range(len(a_list)):
        core_time.append(list_time[i][l_list[i]:r_list[i]])
        core_phase.append(list_phase[i][l_list[i]:r_list[i]])
    return core_time, core_phase


def main():
    ori_epc = '0f-1d'
    filename = r"data\2021-07-18\16-37-33.txt"
    list_epc, list_time, list_phase, __ = ObtainData(
        ori_epc, filename=filename, antenna='9')
    plot_epc, __, __, __ = ObtainData(
        '14 1C', filename=filename, antenna='9')

    fit_epc, core_time, core_phase, l_list, r_list, dim_l_list, dim_r_list, unfit_epc = process(
        list_epc, list_time, list_phase)
    fit_phase, parameter = get_fit(fit_epc, core_time, core_phase)
    pos, order = get_order(fit_epc, parameter)
    get_plot("one", plot_epc, fit_epc, core_time, core_phase, fit_phase, list_time, list_phase,
             pos, order, parameter, unfit_epc)
    if(len(fit_epc) > 10):
        core_time, core_phase = adapt_shape(fit_epc, [list_time[list_epc.index(epc)] for epc in fit_epc], [list_phase[list_epc.index(epc)] for epc in fit_epc], l_list,
                                            r_list, dim_l_list, dim_r_list, parameter)
        fit_phase, parameter = get_fit(fit_epc, core_time, core_phase)
        pos, order = get_order(fit_epc, parameter)
        get_plot("two", plot_epc, fit_epc, core_time, core_phase, fit_phase, list_time, list_phase,
                 pos, order, parameter, unfit_epc)
    plt.show()


if __name__ == '__main__':
    main()
