import os
import multiprocessing
import socket
import jpype
import jpype.imports
from manage_data import *


def get_epc_information():
    # tcp设置
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp绑定IP与端口
    tcp_socket.bind(("127.0.0.1", 1234))
    # tcp开始侦听
    tcp_socket.listen()
    print('Wait for connection ...')
    tcp_client, addr = tcp_socket.accept()
    # 连接成功
    print('Connected')
    while True:  # 接收数据并解码
        data = tcp_client.recv(1024).decode()


def link_reader():

    jar_path = os.path.join(os.path.abspath(
        '.'), 'lib/RFID_FMS.jar')
    jpype.startJVM(jpype.getDefaultJVMPath(), "-ea",
                   "-Djava.class.path=%s" % jar_path, convertStrings=False)

    reader = jpype.JClass('com.rfid.GetInfomationOfRssiAndPhase')
    reader = reader()

    reader.main([""])
    jpype.shutdownJVM()


def main():
    t1 = multiprocessing.Process(target=get_epc_information)
    t2 = multiprocessing.Process(target=link_reader)

    t1.start()
    t2.start()
    t2.join()
    archive_data()


if __name__ == '__main__':
    main()
