"""
相位拟合，将几段曲线拼凑后进行多项式拟合
2021/05/29
by LinXuan
"""
import os
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def get_data(file):
    "从文件中读取相位数据"
    with open(file) as f:
        lines = f.readlines()
        data = [float(line.split('#')[-2]) for line in lines]  # 只取每一行数据的相位信息
        return data


def visualization(*alldata):
    "可视化数据"
    colors = list(mcolors.TABLEAU_COLORS.keys())  # 颜色变化
    n = len(alldata)
    for i in range(0, n):
        data = alldata[i]
        plt.subplot(1, n, i + 1)
        x = list(range(0, len(data)))
        plt.plot(x, data, color=mcolors.TABLEAU_COLORS[colors[i]], marker='*', linestyle=':')
    plt.show()


def process(olddata):
    "粘合数据范围"
    size = len(olddata)  # 数据量的大小
    newdata = [0] * size
    ct = 0
    for i in range(1, size):
        if(olddata[i] - olddata[i - 1] < -5):
            ct += 1
        elif(olddata[i] - olddata[i - 1] > 5):
            ct -= 1
        newdata[i] = olddata[i] + ct * math.pi * 2
    return newdata


def regression(time, data):
    "多项式回归， 返回拟合后的数据和多项式参数"
    parameter = np.polyfit(time, data, 2)
    func = np.poly1d(parameter)
    data_fit = func(time)
    return data_fit, parameter


def main():
    "测试功能"
    filename = "RFID/data002.txt"
    data = get_data(filename)
    # visualization(data)
    data_process = process(data)
    time = list(range(0, len(data)))
    data_fit, __ = regression(time, data_process)
    visualization(data, data_process, data_fit)


def PhaseFitting(time, data):
    """
    相位拟合 reutrn data_fit[], center, parameter[a,b,c]
    """
    data_process = process(data)
    data_fit, parameter = regression(time, data_process)
    return data_fit, -parameter[1]/(2*parameter[0]), parameter

if __name__ == "__main__":
    main()
