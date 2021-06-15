import socket
import matplotlib.pyplot as plt
import time

# tcp设置
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# tcp绑定IP与端口
tcp_socket.bind(('192.168.3.32', 1234))
# tcp开始侦听
tcp_socket.listen()

ListEpc = []            # EPC列表
ListTime = []           # Time列表
ListRssi = []           # RSSI列表
ListPhase = []          # PHASE列表

FirstTime = 0           # 初始化一个开始时间，每次获得的开始时间不同
# 等待tcp建立连接
print('Wait for connection ...')
tcp_client, addr = tcp_socket.accept()
plt.figure(1)
plt.ion()  # 开启interactive mode 成功的关键函数

while True:
    data = tcp_client.recv(1024).decode()   # 接收数据并解码
    TagInfo = data.split('#')
    if len(TagInfo) != 4:                   # 接收的TagInfo长度为4，分别为EPC, Time, Rssi, Phase，错误则开启下一个循环
        continue
    elif float(TagInfo[2]) == 0:            # 若接收的Rssi为0，则接收错误，开启下一个循环
        continue
    else:
        if FirstTime == 0:                   # 第一次接收到Tag信息，将FirstTime初始化
            FirstTime = int(TagInfo[1])
        if TagInfo[0] not in ListEpc:       # 若出现新标签，将新标签加入列表，为新标签创建各信息列表
            ListEpc.append(TagInfo[0])
            ListTime.append([])
            ListRssi.append([])
            ListPhase.append([])
        TagIndex = ListEpc.index(TagInfo[0])        # 找出当前Tag所处列表位置

        # 将相应Tag信息入列表
        ListTime[TagIndex].append((int(TagInfo[1]) - FirstTime) / 1000000)        # 对时间处理为精度0.1s
        ListRssi[TagIndex].append(float(TagInfo[2]))
        ListPhase[TagIndex].append(float(TagInfo[3]))

        if len(ListTime[TagIndex]) > 35:       # 若时间大于等于35个，则将最先TagInfo出列表,保证列表中最多35个
            ListTime[TagIndex].pop(0)
            ListRssi[TagIndex].pop(0)
            ListPhase[TagIndex].pop(0)

        # 设置x为Time，y分别为Rssi，Phase
        x_time = ListTime[TagIndex]
        y_rssi = ListRssi[TagIndex]
        y_phase = ListPhase[TagIndex]

        # 实时画图部分
        plt.clf()  # 清空画布上的所有内容
        plt.plot(x_time, y_rssi, '-r', x_time, y_phase, '-y')
        plt.pause(0.001)

tcp_client(close)
