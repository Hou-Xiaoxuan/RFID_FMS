'''
Author: LinXuan
Date: 2021-09-27 07:39:59
Description:
LastEditors: LinXuan
LastEditTime: 2021-09-27 11:29:27
FilePath: /RFID_FMS/pysrc/CNN/RNN_LSTM_model.py
'''
import torch
import torch.nn as nn
import numpy as np
from CNN.GetData import read_json
# 超参数
TIME_STEP = 800
INPUT_SIZE = 2
BATCH_SIZE = 5
LR = 0.01
EPOCH = 100

FILE_LIST = [
    "/Data/Dataset/18-10-28.json"[1:],
    "/Data/Dataset/18-19-32.json"[1:],
    "/Data/Dataset/18-23-27.json"[1:],
    "/Data/Dataset/18-26-44.json"[1:]
]


def get_data():
    x_lsit = []
    y_list = []
    for filename in FILE_LIST:
        x, y = read_json(filename)
        x_lsit.append(x)
        y_list.append(y)
    X = np.concatenate(tuple([i for i in x_lsit]), axis=0)
    # print(X.size)
    Y = np.concatenate(tuple([i for i in y_list]), axis=0)
    # print(Y.size)
    return X, Y
# run model


class RNN(nn.Module):
    def __init__(self):
        super(RNN, self).__init__()

        # TODO:使用LSTM有各种问题，RNN可以直接有运行
        self.rnn = nn.RNN(
            input_size=INPUT_SIZE,
            hidden_size=64,
            num_layers=1,
            batch_first=True,
        )
        self.out = nn.Linear(64, 1)

    def forward(self, x, h_state):
        r_out, h_state = self.rnn(x, h_state)
        outs = []
        for time_step in range(r_out.size(1)):
            outs.append(self.out(r_out[:, time_step, :]))
        # torcy.stack() 将多个独立的tensor量整合到一起
        return torch.stack(outs), h_state


def train(train_x, train_y):

    # 展开训练
    rnn = RNN()
    optimizer = torch.optim.Adam(rnn.parameters(), lr=LR)  # 优化器
    loss_func = nn.MSELoss()  # 平凡熵函数

    train_data = torch.utils.data.dataset.TensorDataset(train_x, train_y)  # 训练数据
    train_loader = torch.utils.data.DataLoader(dataset=train_data, batch_size=BATCH_SIZE, shuffle=True)  # data_loader进行批处理
    h_state = None
    for epoch in range(EPOCH):
        show_loss = 0
        for step, (bx, by) in enumerate(train_loader):
            # print(type(bx), type(by))
            output, h_state = rnn(bx, h_state)
            # very important:
            # h_state = h_state.data    # repack the hidden state, break the connection from last iteration
            h_state = h_state.detach()
            loss = loss_func(output, by)
            loss.backward(retain_graph=True)  # TODO: 有没有解决的错误，不应该有参数
            optimizer.step()
            show_loss = loss.detach().numpy()
        print(f"After epoch {epoch}.")

    # # 不用批处理
    # h_state = None
    # for epoch in range(EPOCH):
    #     output, h_state = rnn(train_x, h_state)
    #     h_state = h_state.detach()
    #     loss = loss_func(output, train_y)
    #     loss.backward(retain_graph=True)
    #     optimizer.step()

    # 保存网络
    torch.save(rnn, '/pysrc/CNN/rnn.pkl'[1:])


# 准确率
def main():
    # 获取数据
    x_np, y_np = get_data()
    train_x = torch.FloatTensor(x_np)
    train_y = torch.FloatTensor(y_np)
    # train(train_x, train_y)
    rnn = torch.load('/pysrc/CNN/rnn.pkl'[1:])
    # print(rnn)
    train_output, __ = rnn(train_x, None)
    pred_y = torch.max(train_output, 0)[1].data.numpy()
    pred_y = pred_y.reshape((60, ))
    print(pred_y)
    target_y = torch.max(train_y, 1)[1].data.numpy()
    print(target_y)


if __name__ == "__main__":
    main()
