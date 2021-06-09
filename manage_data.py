#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Time    : 2021/05/18
@Author  : xvrong
@File    : manage_data.py
@Function: 整理数据文件和画图文件
'''
import time
import os
import shutil
import re


def mkdir(path):
    folder = os.path.exists(path)
    # 判断是否存在文件夹如果不存在则创建为文件夹
    if not folder:
        # makedirs 创建文件时如果路径不存在会创建这个路径
        os.makedirs(path)


def main():
    # 数据文件名
    file_path = 'data.txt'
    # 判断数据是否存在，不存在，直接退出
    if (os.path.exists(file_path)):
        # 获取时间
        cur_time = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        # 分割
        [cur_day, cur_time] = cur_time.split(' ')
        # 创建名为当前年月日的文件夹
        dir_path = os.path.join('data', cur_day)
        mkdir(dir_path)
        # 通过当前时间为文件命名
        new_name = cur_time + '.txt'

        # 移动文件数据文件
        dest_path = os.path.join(dir_path, new_name)
        shutil.copy(file_path, dest_path)

        # 移动png文件
        file_list = os.listdir()
        png_list = []
        for file in file_list:
            if(file.endswith('.png')):
                png_list.append(file)
        for i in range(0, len(png_list)):
            new_name = cur_time + '-' + str(i) + '.png'
            dest_path = os.path.join(dir_path, new_name)
            shutil.copy(png_list[i], dest_path)


if __name__ == '__main__':
    main()
