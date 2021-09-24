'''
Author: xv_rong
Date: 2021-09-23 21:46:32
LastEditors: xv_rong
LastEditTime: 2021-09-24 21:39:23
Description: 
FilePath: /RFID_FMS/core_v.py
'''

import numpy as np
import math
DOT = 30
JUMP_SHAKE = 4
JUMP_BLOCK = 3
SMALL_SHAKE = 20
NEAR_PI = 1.28


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

# TODO:state


def find_N(k):
    l_tmp, r_tmp = 0, 0
    l, r = [], []
    state = 0
    for i in range(0, len(k) - 1, 1):
        if state == 0:
            if k[i] < k[i + 1]:
                state = 1
        elif state == 1:
            if k[i] > k[i + 1]:
                state = 2
                l_tmp = i
        elif state == 2:
            if k[i] < k[i + 1]:
                state = 1
                r_tmp = i + 1
                if r_tmp - l_tmp > 15:
                    l.append(l_tmp)
                    r.append(r_tmp)
    return l, r

# TODO:state


def find_dec(k):
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


def core_v(time, phase):

    up_small_shake(phase, SMALL_SHAKE, JUMP_SHAKE, NEAR_PI)
    up_core_block(phase, JUMP_BLOCK)

    k, b = derivation(time, phase, DOT)
    time_one = time[0 + DOT: len(time) - DOT]

    l, r = find_N(k)
    if len(l) == 0:
        l, r = find_dec(k)

    flag, l, r = select_boundary(k, time_one, l, r)
    return flag, time[l - 10 + DOT: r + 10 + DOT], phase[l - 10 + DOT: r + 10 + DOT]
