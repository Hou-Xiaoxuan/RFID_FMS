#!/usr/bin/python3
import threading
import socket
import matplotlib.pyplot as plt
import time


ListEpc = ["FFFF 0000 0000 0000 0000 0000",
           "FFFF 0001 0000 0000 0000 0000",
           "FFFF 0002 0000 0000 0000 0000",
           "FFFF 0003 0000 0000 0000 0000",
           "FFFF 0004 0000 0000 0000 0000"
           ]            # EPC列表
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
    print('Connected')
    FirstTime = 0           # 初始化一个开始时间，每次获得的开始时间不同
    while True:
        data = tcp_client.recv(1024).decode()   # 接收数据并解码
        TagInfo = data.split('#')
        mutex.acquire()
        if len(TagInfo) == 5:                   # 接收的TagInfo长度为4，分别为EPC, Time, Rssi, Phase，错误则开启下一个循环
            if int(TagInfo[2] != 0):  # 若接收的Rssi为0，则接收错误，开启下一个循环
                if (TagInfo[0] in ListEpc):
                    if FirstTime == 0:                  # 第一次接收到Tag信息，将FirstTime初始化
                        FirstTime = int(TagInfo[1])
                    TagIndex = ListEpc.index(
                        TagInfo[0])        # 找出当前Tag所处列表位置
                    # 将相应Tag信息入列表
                    ListTime[TagIndex].append(
                        (int(TagInfo[1]) - FirstTime)/1000000)        # 对时间处理为精度0.1s
                    ListRssi[TagIndex].append(float(TagInfo[2]))
                    ListPhase[TagIndex].append(float(TagInfo[3]))
                    # 若时间大于等于35个，则将最先TagInfo出列表,保证列表中最多35个
                    if len(ListTime[TagIndex]) > 35:
                        ListTime[TagIndex].pop(0)
                        ListRssi[TagIndex].pop(0)
                        ListPhase[TagIndex].pop(0)
        mutex.release()


def plot():
    plt.ion()  # 开启interactive mod
    color = ['blue', 'red', 'green', 'pink', 'purple', 'yellow']  # 曲线颜色
    while True:
        mutex.acquire()
        for TagIndex in range(0, len(ListEpc)):
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
        mutex.release()
        plt.pause(0.1)


mutex = threading.Lock()


def main():

    t1 = threading.Thread(target=get_tag_information)
    t2 = threading.Thread(target=plot)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


if __name__ == "__main__":
    # execute only if run as a script
    main()
