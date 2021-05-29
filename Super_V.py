#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2021/05/29
@Author  : xv_rong
@File    : Super_V.py
@Function: 拟合Super-V区
'''
from matplotlib.pyplot import pause, title
import numpy as np
listen_epc = [
    "FFFF 0000 0000 0000 0000 0000", "FFFF 0001 0000 0000 0000 0000",
    "FFFF 0002 0000 0000 0000 0000", "FFFF 0003 0000 0000 0000 0000",
]  # 实验中监控的标签列表
list_epc = []            # EPC列表
list_time = []           # Time列表
list_rssi = []           # RSSI列表
list_phase = []          # PHASE列表
first_time = 0           # 初始化一个开始时间，每次获得的开始时间不同
color = ['-b', '-r', '-g', '-k', '-m', '-y']  # 曲线颜色
with open("./src/21-05-19-4标签顺序检测数据-ffff0000-ffff0003.txt") as lines:
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
                # ListPhase.append([])
            tag_index = list_epc.index(tag_info[0])        # 找出当前Tag所处列表位置

            # 将相应Tag信息入列表
            list_time[tag_index].append(
                (int(tag_info[1]) - first_time) / 1000000)        # 对时间处理为精度0.1s
            list_rssi[tag_index].append(float(tag_info[2]))
            list_phase[tag_index].append(float(tag_index[3]))

    """数据拟合与画图"""

    import matplotlib.pyplot as plt
    for now_epc in range(0, len(list_epc)):
        for j in range(0, range(now_epc)):
            down_cycle = 0
