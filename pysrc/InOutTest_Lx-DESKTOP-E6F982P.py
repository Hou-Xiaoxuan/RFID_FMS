"""
RFID 进出检测脚本，实时同步
2021/05/18
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
ValidEpc = set(["0000 002D 2000 0000 0000 0000", "0000 0034 2000 0000 0000 0000",
                "0000 002E 2000 0000 0000 0000", "0000 0035 2000 0000 0000 0000",
                "0000 002F 2000 0000 0000 0000", "0000 0036 2000 0000 0000 0000",
                "0000 0030 2000 0000 0000 0000", "0000 0037 2000 0000 0000 0000",
                "0000 0031 2000 0000 0000 0000", "0000 0038 2000 0000 0000 0000",
                "0000 0032 2000 0000 0000 0000", "0000 0039 2000 0000 0000 0000",
                "0000 0033 2000 0000 0000 0000", "0000 003A 2000 0000 0000 0000",
                "0000 003B 2000 0000 0000 0000", ])  # 合法的标签识别
EpcStatue = []  # EPC状态标识
EpcListen = []  # 正在进行进出库的标签


class Statue(Enum):
    IN = 0
    OUT = 1
    NoN = -1


class Ant_Index(Enum):
    IN = 1
    OUT = 9


"核心工作代码"


def work(tcp_client):
    LastUpdateTime = 0
    while(True):
        NowTime = time.time()  # 当前的计算机时间
        if(NowTime - LastUpdateTime > 1):  # 超过10s没有输出，输出一次标签状态
            LastUpdateTime = NowTime
            for index in EpcListen:
                print("%3s" % index[7:9], end=' ')
            print("")
            for statue in EpcStatue:
                print("%3s" % statue, end=' ')
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
        if(TagInfo[0] not in EpcListen):  # 对于新检测到的标签，加入监听列表并初始化Listen状态
            EpcListen.append(TagInfo[0])
            EpcStatue.append(Statue.NoN.value)

        Change_Flag = True  # 标记是否有标签状态变化
        TagIndex, TagAnti = EpcListen.index(
            TagInfo[0]), int(TagInfo[4])  # 得到标签再列表中的下表和时间
        if(EpcStatue[TagIndex] != Statue.OUT.value and TagAnti == Ant_Index.OUT.value):  # 标签出库
            EpcStatue[TagIndex] = Statue.OUT.value
        elif(EpcStatue[TagIndex] != Statue.IN.value and TagAnti == Ant_Index.IN.value):  # 标签入库
            EpcStatue[TagIndex] = Statue.IN.value
        else:
            Change_Flag = False  # 未发生状态改变

        if(NowTime - LastUpdateTime > 1 and Change_Flag == True):
            # 如果上次改变大于5秒或10秒没有输出，则输出显示一次
            LastUpdateTime = NowTime
            for index in EpcListen:
                print("%3s" % index[7:9], end=' ')
            print("")
            for statue in EpcStatue:
                print("%3s" % statue, end=' ')
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
