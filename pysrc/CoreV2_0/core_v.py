'''
Author: xv_rong
Date: 2021-09-23 21:46:32
LastEditors: xv_rong
LastEditTime: 2021-10-31 14:34:32
Description: 
FilePath: /RFID_FMS/pysrc/CoreV2_0/core_v.py
'''

import numpy as np
import math
DOT = 30
DOT2 = 10
TURN = 3

JUMP_SHAKE = 4
JUMP_BLOCK = 3
SMALL_SHAKE = 20
NEAR_PI = 1.28
DEBUG = True


def up_small_shake(data, small=20, jump=4, near_PI=1.28):
    l, r = 0, 0
    state = 0
    for i in range(1, len(data)):
        if data[i] - data[i - 1] < -jump:  # i-1到i处出现跳跃
            state = 1
            l = i
        elif state == 1:
            if data[i] - data[i - 1] > jump:
                state = 0
                r = i
                if r - l < small and data[i] < near_PI:
                    for i in range(l, r):
                        data[i] = 2 * math.pi + data[i]


def up_core_block(data, jump=3):
    l, r = 0, 0
    state = 0
    for i in range(1, len(data)):
        if data[i] - data[i - 1] < -jump:  # i-1到i处出现跳跃
            state = 1
            l = i
        if state == 1:
            if data[i] - data[i - 1] > jump:
                state = 0
                r = i
                for i in range(l, r):
                    data[i] = 2 * math.pi + data[i]


def derivation(time, phase, dot):
    k, b = [], []
    for i in range(dot, len(time) - dot, 1):
        __, parameter = regression(
            time[i - dot: i + dot + 1], phase[i - dot: i + dot + 1], 1)
        k.append(parameter[0])
        b.append(parameter[1])
    return k, b


def regression(time, phase, degree):
    parameter = np.polyfit(time, phase, degree)
    func = np.poly1d(parameter)
    phase_fit = func(time)
    return phase_fit, parameter


def find_dec(k):
    k.append(math.inf)
    l_tmp, r_tmp = 0, 0
    l, r = [], []
    state = 0
    for i in range(0, len(k) - 1, 1):
        if state == 0:
            if k[i] > k[i + 1]:
                state = 1
                l_tmp = i
        elif state == 1:
            if k[i] < k[i + 1]:
                state = 0
                r_tmp = i + 1
                if r_tmp - l_tmp > 15:
                    l.append(l_tmp)
                    r.append(r_tmp)
    k.pop()  # r可能越界,但是可以处理
    return l, r


def select_boundary(k, time, l, r):
    l_ans, r_ans = 0, 0
    for i in range(len(l)):
        __, [a, b] = regression(time[l[i]: r[i]], k[l[i]: r[i]], 1)
        x1 = a * time[l[i]] + b
        x2 = a * time[r[i] - 1] + b
        if x1 > 0 and x2 < 0:
            if r[i] - l[i] > r_ans - l_ans:
                l_ans, r_ans = l[i], r[i]
    return bool(r_ans - l_ans), l_ans, r_ans


def compensate_DOT(l, r, k, time, DOT, DOT2, TURN):
    # 计算应当补偿多少个点
    if (l - DOT2 + 1 >= 0 and l + 1 <= len(k)):
        __, parameterl = regression(
            time[l - DOT2 + 1: l + 1], k[l - DOT2 + 1: l + 1], 1)
        if parameterl[0] > TURN:
            l = l - DOT
        else:
            l = l - DOT // 2
    else:
        l = l - DOT // 2

    if (r - 1 >= 0 and r + DOT2 - 1 <= len(k)):
        __, parameterr = regression(
            time[r - 1: r + DOT2 - 1], k[r - 1: r + DOT2 - 1], 1)
        if parameterr[0] > TURN:
            r = r + DOT
        else:
            r = r + DOT // 2
    else:
        r = r + DOT // 2
    return l, r


def limit_PI(l, r, phase):
    # 将phase的范围限定在做高点左右一个PI内
    index = np.argmax(phase[l:r])
    index += l
    top = phase[index]

    for i in range(index - 1, l - 1, -1):
        if phase[i] >= top - 2 * math.pi:
            l = i

    for i in range(index, r, 1):
        if phase[i] >= top - 2 * math.pi:
            r = i

    return l, r


def core_v(time, phase):

    up_small_shake(phase, SMALL_SHAKE, JUMP_SHAKE, NEAR_PI)
    up_core_block(phase, JUMP_BLOCK)

    k, b = derivation(time, phase, DOT)
    time_one = time[0 + DOT: len(time) - DOT]
    l, r = find_dec(k)
    flag, l, r = select_boundary(k, time_one, l, r)

    if DEBUG:
        import matplotlib.pyplot as plt
        plt.scatter(time, phase, c='green')
        plt.plot(time_one, k, c='orange')
        plt.scatter([time_one[l], time_one[r - 1]],
                    [k[l], k[r - 1]], c='black')

        k2, b2 = derivation(k, time_one, DOT2)
        time_two = time_one[0 + DOT2: len(time_one) - DOT2]
        plt.scatter(time_two, k2, c='blue')

        plt.plot([x for x in time], [0 for i in time], c='black')

        plt.plot([time_one[l] for x in range(100)], [
                 i / 100 for i in range(-300, 600, 9)], c='black')
        plt.plot([time_one[r - 1] for x in range(100)],
                 [i / 100 for i in range(-300, 600, 9)], c='black')
        plt.ylim(-2*math.pi, 4*math.pi)

        if (l - DOT2 + 1 >= 0 and r + DOT2 - 1 <= len(k)):
            __, parameterl = regression(
                time_one[l - DOT2 + 1: l + 1], k[l - DOT2 + 1: l + 1], 1)
            __, parameterr = regression(
                time_one[r - 1: r + DOT2 - 1], k[r - 1: r + DOT2 - 1], 1)

            plt.title(str(parameterl[0]) + '  ' + str(parameterr[0]))

        plt.rcParams['figure.figsize'] = 100, 100
        if not flag:
            plt.show()
    if not flag:
        return flag, time[l: r], phase[l: r]

    l, r = compensate_DOT(l, r, k, time_one, DOT, DOT2, TURN)

    l, r = l + DOT, r + DOT

    l, r = limit_PI(l, r, phase)

    if DEBUG:
        plt.scatter(time[l: r],
                    phase[l: r], c='red')
        plt.show()

    return flag, time[l: r], phase[l: r]

# def find_N(k):
#     l_tmp, r_tmp = 0, 0
#     l, r = [], []
#     state = 0
#     for i in range(0, len(k) - 1, 1):
#         if state == 0:
#             if k[i] < k[i + 1]:
#                 state = 1
#         elif state == 1:
#             if k[i] > k[i + 1]:
#                 state = 2
#                 l_tmp = i
#         elif state == 2:
#             if k[i] < k[i + 1]:
#                 state = 1
#                 r_tmp = i + 1
#                 if r_tmp - l_tmp > 15:
#                     l.append(l_tmp)
#                     r.append(r_tmp)
#     return l, r
