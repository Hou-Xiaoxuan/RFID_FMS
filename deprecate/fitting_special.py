from matplotlib.pyplot import pause, title
import numpy as np
ListenEpc = [
    "FFFF 0000 0000 0000 0000 0000", "FFFF 0001 0000 0000 0000 0000",
    "FFFF 0002 0000 0000 0000 0000", "FFFF 0003 0000 0000 0000 0000",
]  # 实验中监控的标签列表
ListEpc = []            # EPC列表
ListTime = []           # Time列表
ListRssi = []           # RSSI列表
# ListPhase = []          # PHASE列表
FirstTime = 0           # 初始化一个开始时间，每次获得的开始时间不同
color = ['-b', '-r', '-g', '-k', '-m', '-y']  # 曲线颜色
with open("./data.txt") as lines:
    """
    数据处理部分
    分割后的数据： Epc-Time-Rssi-Phase
    """

    for line in lines:
        TagInfo = line.split('#')
        if len(TagInfo) != 5:                   # 接收的TagInfo长度为4，分别为EPC, Time, Rssi, Phase，错误则开启下一个循环
            # print(TagInfo)
            continue
        elif float(TagInfo[2]) == 0.0:            # 若接收的Rssi为0，则接收错误，开启下一个循环
            continue
        elif TagInfo[0] not in ListenEpc:
            continue
        else:
            # print(TagInfo)
            if FirstTime == 0:                   # 第一次接收到Tag信息，将FirstTime初始化
                FirstTime = int(TagInfo[1])
            if TagInfo[0] not in ListEpc:       # 若出现新标签，将新标签加入列表，为新标签创建各信息列表
                ListEpc.append(TagInfo[0])
                ListTime.append([])
                ListRssi.append([])
                # ListPhase.append([])
            TagIndex = ListEpc.index(TagInfo[0])        # 找出当前Tag所处列表位置

            # 将相应Tag信息入列表
            ListTime[TagIndex].append(
                (int(TagInfo[1]) - FirstTime) / 1000000)        # 对时间处理为精度0.1s
            ListRssi[TagIndex].append(float(TagInfo[2]))
            # ListPhase[TagIndex].append(float(TagInfo[3]))

    """数据拟合与画图"""

    import matplotlib.pyplot as plt
    lenth = len(ListEpc)
    for i in range(0, lenth):
        TagIndex = i
        # 设置x为Time，y分别为Rssi，Phase
        x_time = ListTime[TagIndex]
        y_rssi = ListRssi[TagIndex]
        # y_phase = ListPhase[TagIndex]

        parameter_rssi = np.polyfit(x_time, y_rssi, 3)
        # parameter_phase = np.polyfit(x_time, y_phase, 3)
        func_rssi = np.poly1d(parameter_rssi)
        # func_phase = np.poly1d(parameter_phase)
        y_rssi_fit = func_rssi(x_time)
        y_rssi_fit = y_rssi_fit.tolist()
        # y_phase_fit = func_phase(x_time)
        # y_phase_fit = y_phase_fit.tolist()

        # plt.subplot(1, lenth, i+1)
        plt.plot(x_time, y_rssi_fit, color[i])
        # plt.scatter(x_time, y_rssi, s=10, c="red", marker=".", alpha=1)
        # plt.title("Rssi")
    plt.legend(ListEpc, loc='lower left',
               bbox_to_anchor=(0.77, 0.2), fontsize='xx-large')
    plt.show()
