"""
RFID 进出检测脚本，实时同步
2021、05/18
by LinXuan
"""
import socket
import time
from enum import Enum


def connect():
    "建立连接"
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # tcp设置
    tcp_socket.bind(('127.0.0.1', 1234))  # IP，端口绑定
    tcp_socket.listen()  # 开始侦听
    print('Wait for connection ...')
    tcp_client, addr = tcp_socket.accept()
    print("Successful connect with ", addr)
    return tcp_client


"变量定义"
ValidEpc = set(["FFFF 0000 0000 0000 0000 0000", "FFFF 0001 0000 0000 0000 0000",
                "FFFF 0002 0000 0000 0000 0000", "FFFF 0003 0000 0000 0000 0000",
                "FFFF 0004 0000 0000 0000 0000", "FFFF 0005 0000 0000 0000 0000",
                "FFFF 0006 0000 0000 0000 0000", "FFFF 0007 0000 0000 0000 0000",
                "FFFF 0008 0000 0000 0000 0000", "FFFF 0009 0000 0000 0000 0000",
                "FFFF 0010 0000 0000 0000 0000", "FFFF 0011 0000 0000 0000 0000",
                "FFFF 0012 0000 0000 0000 0000", "FFFF 0013 0000 0000 0000 0000",
                "FFFF 0014 0000 0000 0000 0000", "FFFF 0015 0000 0000 0000 0000",
                "FFFF 0016 0000 0000 0000 0000", "FFFF 0017 0000 0000 0000 0000",
                "FFFF 0018 0000 0000 0000 0000", "FFFF 0019 0000 0000 0000 0000"])  # 合法的标签识别
EpcStatue = []  # EPC状态标识
EpcListen = []  # 正在进行进出库的标签


class Statue(Enum):
    IN = 0
    OUT = 1
    NoN = -1


class Ant_Index(Enum):
    ANT_IN = 1
    ANT_OUT = 9


"核心工作代码"


def work(tcp_client):
    LastUpdateTime = 0
    while(True):
        NowTime = time.time()  # 当前的计算机时间
        if(LastUpdateTime-NowTime > 10):  # 超过10s没有输出，输出一次标签状态
            LastUpdateTime = NowTime
            for index in EpcStatue:
                print("%3d" % index, end=' ')
            print("")
            for statue in EpcStatue:
                print("%3s", statue, end=' ')
            print("")

        data = tcp_client.recv(1024).decode()  # 接收数据并解码
        TagInfo = data.split('#')  # 分割数据
        # 排除异常情况
        if len(TagInfo) != 5:  # 接收的TagInfo长度为4，分别为EPC, Time, Rssi, Phase，错误则开启下一个循环
            continue
        elif float(TagInfo[2]) == 0.0:
            continue  # 若接收的Rssi为0，则接收错误，开启下一个循环
        elif TagInfo[0] not in ValidEpc:
            continue  # 标签不在库中，则接收错误，开启下一个循环
        if(TagInfo[2] not in EpcListen):  # 对于新检测到的标签，加入监听列表并初始化Listen状态
            EpcListen.append(TagInfo[0])
            EpcStatue.append(Statue['NoN'])

        Change_Flag = True  # 标记是否有标签状态变化
        TagIndex, TagAnti = EpcListen.index(
            TagInfo[0]), TagInfo[4]  # 得到标签再列表中的下表和时间
        if(EpcStatue[TagIndex] != Statue['OUT'] and TagAnti == Ant_Index['OUT']):  # 标签出库
            EpcStatue[TagIndex] = Statue['OUT']
        elif(EpcStatue[TagIndex] != Statue['IN'] and TagAnti == Ant_Index['IN']):  # 标签入库
            EpcStatue[TagIndex] = Statue['IN']
        else:
            Change_Flag = False  # 未发生状态改变

        if(NowTime - LastUpdateTime > 5 and Change_Flag == True):
            # 如果上次改变大于5秒或10秒没有输出，则输出显示一次
            LastUpdateTime = NowTime
            for index in EpcStatue:
                print("%3d" % index, end=' ')
            print("")
            for statue in EpcStatue:
                print("%3s", statue, end=' ')
            print("")


if __name__ == "__main__":
    tcp_client = connect()
    try:
        work(tcp_client)
    except EOFError:
        print("程序结束，正常退出")
        tcp_client.close()
    finally:
        print("程序异常退出")
        tcp_client.close()
