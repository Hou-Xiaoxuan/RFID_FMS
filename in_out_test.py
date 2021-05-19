import socket
import time
from enum import Enum
TIME_OUT = 1    # 1s未被检测到，则判断档案状态


class statue_list(Enum):
    IN = 0
    OUT = 1


class antennaPort_list(Enum):
    ONE = 1
    NINE = 9


# tcp设置
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# tcp绑定IP与端口
tcp_socket.bind(('127.0.0.1', 1234))
# tcp开始侦听
tcp_socket.listen()
# EPC列表 需要初始化
Epc_list = [
    "FFFF 0000 0000 0000 0000 0000", "FFFF 0001 0000 0000 0000 0000",
    "FFFF 0002 0000 0000 0000 0000", "FFFF 0003 0000 0000 0000 0000",
    "FFFF 0004 0000 0000 0000 0000", "FFFF 0005 0000 0000 0000 0000",
    "FFFF 0006 0000 0000 0000 0000", "FFFF 0007 0000 0000 0000 0000",
    "FFFF 0008 0000 0000 0000 0000", "FFFF 0009 0000 0000 0000 0000",
    "FFFF 0010 0000 0000 0000 0000", "FFFF 0011 0000 0000 0000 0000",
    "FFFF 0012 0000 0000 0000 0000", "FFFF 0013 0000 0000 0000 0000",
    "FFFF 0014 0000 0000 0000 0000", "FFFF 0015 0000 0000 0000 0000",
    "FFFF 0016 0000 0000 0000 0000", "FFFF 0017 0000 0000 0000 0000",
    "FFFF 0018 0000 0000 0000 0000", "FFFF 0019 0000 0000 0000 0000",
    "FFFF 0020 0000 0000 0000 0000", "FFFF 0021 0000 0000 0000 0000",
    "FFFF 0022 0000 0000 0000 0000", "FFFF 0023 0000 0000 0000 0000",
    "FFFF 0024 0000 0000 0000 0000", "FFFF 0025 0000 0000 0000 0000",
    "FFFF 0026 0000 0000 0000 0000", "FFFF 0027 0000 0000 0000 0000",
    "FFFF 0028 0000 0000 0000 0000", "FFFF 0029 0000 0000 0000 0000"
]
# 初始化标签 在库中
Epc_statue = [statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN,
              statue_list.IN, statue_list.IN]
Epc_listen = []        # 正在进行进出库的标签
Epc_timer = []         # 最后一次被检测到的时间
Epc_anti = []          # 最后一次检测所用的天线，判断标签进出库状态
cnt = 0
# 等待tcp建立连接
print('Wait for connection ...')
tcp_client, addr = tcp_socket.accept()
print('Connected')
time_print_start = 0
elen = len(Epc_list)
while True:
    i = 0
    now_time = time.time()
    if time_print_start == 0:
        time_print_start = now_time
    while i < len(Epc_listen):
        # if (now_time - Epc_timer[i] > TIME_OUT):
        Epc_timer.pop(i)
        Epc_tmp = Epc_listen.pop(i)
        index = Epc_list.index(Epc_tmp)
        antennaPort = Epc_anti.pop(i)
        staute_before = Epc_statue[index]
        i = i - 1
        if (antennaPort == antennaPort_list.ONE.value):
            Epc_statue[index] = statue_list.IN.value
        if (antennaPort == antennaPort_list.NINE.value):
            Epc_statue[index] = statue_list.OUT.value
        i = i + 1
    if now_time - time_print_start > TIME_OUT:
        print(cnt)
        cnt = cnt + 1
        time_print_start = now_time
        for i in range(0, elen):
            print("%2d" % (i), end=' ')
        print("")
        for i in range(0, elen):
            if Epc_statue[i] == statue_list.IN.value:
                print("IN", end=' ')
            else:
                print("OT", end=' ')
        print("")
    data = tcp_client.recv(1024).decode()   # 接收数据并解码
    TagInfo = data.split('#')
    # 确认单位
    if len(TagInfo) != 5:                   # 接收的TagInfo长度为4，分别为EPC, Time, Rssi, Phase，错误则开启下一个循环
        continue
    elif float(TagInfo[2]) == 0.0:          # 若接收的Rssi为0，则接收错误，开启下一个循环
        continue
    elif TagInfo[0] not in Epc_list:
        continue                            # 标签不在库中，则接收错误，开启下一个循环
    elif TagInfo[0] not in Epc_listen:
        Epc_listen.append(TagInfo[0])
        Epc_timer.append(now_time)
        Epc_anti.append(int(TagInfo[4]))
    else:
        index = Epc_listen.index(TagInfo[0])
        Epc_timer[index] = now_time
        Epc_anti[index] = int(TagInfo[4])
