#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2021/05/18
@Author  : xvrong
@File    : manage_data.py
@Function: 整理数据文件
'''
import time
import os
import shutil


def mkdir(path):
    folder = os.path.exists(path)
    # 判断是否存在文件夹如果不存在则创建为文件夹
    if not folder:
        # makedirs 创建文件时如果路径不存在会创建这个路径
        os.makedirs(path)


def main():
    # 临时数据文件名
    file_path = 'data.txt'
    # 判断数据是否存在，不存在，直接退出
    if (os.path.exists(file_path)):
        # 获取时间
        now = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        # 分割
        [day, hour] = now.split(' ')
        # 创建名为当前年月日的文件夹
        dir_path = os.path.join('data', day)
        mkdir(dir_path)
        # 通过当前时间为文件命名
        new_name = hour + '.txt'
        # 移动文件
        file_new_path = os.path.join(dir_path, new_name)
        shutil.move(file_path, file_new_path)


if __name__ == '__main__':
    main()
