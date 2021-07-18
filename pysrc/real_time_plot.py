#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2021/05/29
@Author  : xv_rong
@File    : real_time_plot.py
@Function: 多线程处理，实时画图
'''
import os
import socket
import threading
import time
import jpype
import time
import os
import shutil
import re

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from ObtainData import GenerateListenEpc

# EPC列表
ListEpc = GenerateListenEpc(["1e-2c"])
ListTime = [[] for i in range(0, len(ListEpc))]          # Time列表
ListRssi = [[] for i in range(0, len(ListEpc))]          # RSSI列表
ListPhase = [[] for i in range(0, len(ListEpc))]         # PHASE列表


def get_tag_information():
    # tcp设置
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp绑定IP与端口
    tcp_socket.bind(('127.0.0.1', 1234))
    # tcp开始侦听
    tcp_socket.listen()
    print('Wait for connection ...')
    tcp_client, addr = tcp_socket.accept()
    # 连接成功
    print('Connected')
    FirstTime = 0           # 初始化一个开始时间，每次获得的开始时间不同
    while True:
        data = tcp_client.recv(1024).decode()   # 接收数据并解码
        TagInfo = data.split('#')

        # 接收的TagInfo长度为5，分别为EPC, Time, Rssi, Phase, anti，错误则开启下一个循环
        if len(TagInfo) == 5:
            if int(TagInfo[2] != 0):            # 若接收的Rssi为0，则接收错误，开启下一个循环
                mutex.acquire()                 # 上锁
                if (TagInfo[0][0:9] in ListEpc):
                    if FirstTime == 0:                  # 第一次接收到Tag信息，将FirstTime初始化
                        FirstTime = int(TagInfo[1])
                    TagIndex = ListEpc.index(
                        TagInfo[0][0:9])        # 找出当前Tag所处列表位置
                    # 将相应Tag信息入列表
                    ListTime[TagIndex].append(
                        (int(TagInfo[1]) - FirstTime) / 1000000)        # 对时间处理为精度0.1s
                    ListRssi[TagIndex].append(float(TagInfo[2]))
                    ListPhase[TagIndex].append(float(TagInfo[3]))
                    # 若时间大于等于print_len个，则将最先TagInfo出列表,保证列表中最多print_len个
                    print_len = 30
                    if len(ListTime[TagIndex]) > print_len:
                        ListTime[TagIndex].pop(0)
                        ListRssi[TagIndex].pop(0)
                        ListPhase[TagIndex].pop(0)
                mutex.release()  # 解锁


mutex = threading.Lock()  # 线程锁


def plot():
    plt.ion()  # 开启interactive mod
    colors = list(mcolors.TABLEAU_COLORS.keys())  # 颜色变化
    len_colors = len(colors)
    # figrssi = plt.figure("RSSI")
    # figrssi = figrssi.add_subplot(111)
    figphase = plt.figure("PHASE")
    figphase = figphase.add_subplot(111)
    while True:
        mutex.acquire()  # 上锁
        # plt.figure("RSSI")
        # plt.cla()
        plt.figure("PHASE")
        plt.cla()
        for TagIndex in range(0, len(ListEpc)):
            # 设置x为Time
            x_time = ListTime[TagIndex]
            # y为 Rssi 和 Phase
            # y_rssi = ListRssi[TagIndex]
            y_phase = ListPhase[TagIndex]

            # figrssi.plot(x_time, y_rssi, color[TagIndex] % colorlen)  # 设置y轴范围
            # figrssi.set_ylim(-100, -0)                     # 画图

            figphase.scatter(x_time, y_phase,
                             color=mcolors.TABLEAU_COLORS[colors[TagIndex % len_colors]], marker='*')  # 设置y轴范围
            figphase.set_ylim(0, 7)                          # 画图
            # plt.figure("RSSI")
            # plt.legend([num[7:9] for num in ListEpc], loc='lower left',
            #            bbox_to_anchor=(0.77, 0.2), fontsize='x-large')   # 设置图例
            plt.figure("PHASE")
            plt.legend([num[7:9] for num in ListEpc], loc='best',
                       fontsize='x-large')   # 设置图例
            # plt.ioff()
        mutex.release()                    # 解锁
        plt.pause(0.1)                     # 暂停0.1秒


def start_reader():
    jarpath = os.path.join(os.path.abspath(
        "."), 'E:\\OneDrive\\Projects\\RFID\RFID_FMS\\lib\\RFID_FMS.jar')
    jvmPath = jpype.getDefaultJVMPath()
    jvmArg = '-Dhostname=SpeedwayR-12-BE-43'
    if not jpype.isJVMStarted():
        jpype.startJVM(jvmPath, jvmArg, "-ea",
                       "-Djava.class.path=%s" % (jarpath))
    javaClass = jpype.JClass('GetInfomationOfRssiAndPhase')
    if jpype.isJVMStarted():
        javaClass.start_reader()
        


def main():
    # 获取reader信息线程
    t1 = threading.Thread(target=get_tag_information)
    # 画图线程
    # t2 = threading.Thread(target=plot)
    # reader线程
    t3 = threading.Thread(target=start_reader)
    # 设置为守护线程
    t1.setDaemon(True)
    # t2.setDaemon(True)
    t3.setDaemon(True)
    # 开始获取reader信息线程
    t1.start()
    # 开始画图线程
    # t2.start()
    # 开启reader线程
    t3.start()

    # 阻塞主线程
    t1.join()
    # t2.join()
    t3.join()


if __name__ == "__main__":
    # execute only if run as a script
    main()
