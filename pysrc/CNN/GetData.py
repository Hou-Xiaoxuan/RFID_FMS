'''
Author: LinXuan
Date: 2021-09-26 21:14:24
Description:
LastEditors: LinXuan
LastEditTime: 2021-09-27 08:03:28
FilePath: /RFID_FMS/pysrc/CNN/GetData.py
'''
import numpy as np
import json
# 参数
TIME_STEP = 800
INPUT_SIZE = 2


def read_json(filename):
    with open(filename, "r") as f:
        dic = json.loads(f.read())
    dic = dict(dic)
    m = len(dic)  # 数据大小
    X = np.zeros((m, TIME_STEP, INPUT_SIZE))
    Y = np.zeros((m, TIME_STEP))
    for i in range(m):
        data = dic[str(i)]
        time_data = data["time"]
        X[i, :, 0] = np.hstack((np.array(time_data), np.zeros(TIME_STEP - len(time_data))))
        phase_data = data["phase"]
        X[i, :, 1] = np.hstack((np.array(phase_data), np.zeros(TIME_STEP - len(phase_data))))
        pos_data = data["y"]
        Y[i, pos_data] = 1
    return X, Y
