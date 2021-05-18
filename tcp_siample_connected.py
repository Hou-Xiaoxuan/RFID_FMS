import socket
from typing import List
import matplotlib.pyplot as plt
import time

# tcp设置
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# tcp绑定IP与端口
tcp_socket.bind(('127.0.0.1', 1234))
# tcp开始侦听
tcp_socket.listen()
print('Connected')
OwnEpc = ["FFFF 0005 0000 0000 0000 0000", "FFFF 0001 0000 0000 0000 0000",
          "FFFF 0002 0000 0000 0000 0000", "FFFF 0003 0000 0000 0000 0000",
          "FFFF 0004 0000 0000 0000 0000"]
ListEpc = []            # EPC列表
ListTime = []           # Time列表
ListRssi = []           # RSSI列表
ListPhase = []          # PHASE列表
FirstTime = 0           # 初始化一个开始时间，每次获得的开始时间不同
Fig = []
# 等待tcp建立连接
print('Wait for connection ...')
tcp_client, addr = tcp_socket.accept()
print('Connected')
