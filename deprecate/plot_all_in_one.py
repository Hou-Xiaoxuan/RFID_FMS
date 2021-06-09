#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2021/05/29
@Author  : xv_rong
@File    : plot_all_in_one.py
@Function: 将所有信息在同一个图中画出
'''
import socket
from typing import List
import matplotlib.pyplot as plt
import time

# tcp设置
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# tcp绑定IP与端口
tcp_socket.bind(('127.0.0.1', 1234))
# tcp开始侦听
tcp_socket.listen()
OwnEpc = ["FFFF 0000 0000 0000 0000 0000",
          "FFFF 0001 0000 0000 0000 0000",
          "FFFF 0002 0000 0000 0000 0000",
          "FFFF 0003 0000 0000 0000 0000",
          "FFFF 0004 0000 0000 0000 0000"
          ]
ListEpc = []            # EPC列表
ListTime = []           # Time列表
ListRssi = []           # RSSI列表
ListPhase = []          # PHASE列表
FirstTime = 0           # 初始化一个开始时间，每次获得的开始时间不同
# 等待tcp建立连接
color = ['blue', 'red', 'green', 'pink', 'purple', 'yellow']  # 曲线颜色
print('Wait for connection ...')
tcp_client, addr = tcp_socket.accept()
print('Connected')
plt.ion()  # 开启interactive mode 成功的关键函数
for i in OwnEpc:       # 若出现新标签，将新标签加入列表，为新标签创建各信息列表
    ListEpc.append(i)
    ListTime.append([])
    ListRssi.append([])
    ListPhase.append([])

while True:
    data = tcp_client.recv(1024).decode()   # 接收数据并解码
    TagInfo = data.split('#')
    if len(TagInfo) != 5:                   # 接收的TagInfo长度为4，分别为EPC, Time, Rssi, Phase，错误则开启下一个循环
        continue                            # 若接收的Rssi为0，则接收错误，开启下一个循环
    elif int(TagInfo[2] == 0):
        continue
    elif not (TagInfo[0] in OwnEpc):
        continue
    else:
        if FirstTime == 0:                  # 第一次接收到Tag信息，将FirstTime初始化
            FirstTime = int(TagInfo[1])

        TagIndex = ListEpc.index(TagInfo[0])        # 找出当前Tag所处列表位置

        # 将相应Tag信息入列表
        ListTime[TagIndex].append(
            (int(TagInfo[1]) - FirstTime)/1000000)        # 对时间处理为精度0.1s
        ListRssi[TagIndex].append(float(TagInfo[2]))
        ListPhase[TagIndex].append(float(TagInfo[3]))

        if len(ListTime[TagIndex]) > 35:       # 若时间大于等于35个，则将最先TagInfo出列表,保证列表中最多35个
            ListTime[TagIndex].pop(0)
            ListRssi[TagIndex].pop(0)
            ListPhase[TagIndex].pop(0)

        # 设置x为Time
        x_time = ListTime[TagIndex]
        # y为 Rssi 和 Phase
        y_rssi = ListRssi[TagIndex]
        y_phase = ListPhase[TagIndex]
        figrssi = plt.figure("RSSI")
        figphase = plt.figure("PHASE")
        # 实时画图部分
        figrssi = figrssi.add_subplot(111)
        figrssi.plot(x_time, y_rssi, color[TagIndex])
        figrssi.set_ylim(-70, -0)

        figphase = figphase.add_subplot(111)
        figphase.plot(x_time, y_phase, color[TagIndex])
        figphase.set_ylim(0, 7)
        plt.ioff()
        plt.pause(0.0001)
