# coding=utf-8

import threading

import time

import os


num = 0

count = 10


def modifycount():

    global num

    # 获取当前线程对象

    t = threading.current_thread()

    for index in range(count):

        num += 1

        print('%s,修改num' % (t.name))

        time.sleep(0.1)


def printcount():

    global num

    # 获取当前线程对象

    t = threading.current_thread()

    for index in range(count):

        print('%s,num=%d' % (t.name, num))

        time.sleep(0.1)


if __name__ == "__main__":

    print('pid=%d' % os.getpid())

    # 创建线程，此线程修改全局变量

    t = threading.Thread(target=modifycount)

    # 创建线程，此线程打印全局变量

    t2 = threading.Thread(target=printcount)

    t.start()

    t2.start()

    t.join()

    t2.join()

    print('主线程结束,num=%d' % (num))
