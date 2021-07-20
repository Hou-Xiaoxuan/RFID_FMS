'''
Author: xv_rong
Date: 2021-07-19 21:05:04
LastEditors: xv_rong
LastEditTime: 2021-07-20 11:21:42
Description:
FilePath: \RFID_FMS\pysrc\right_rate.py
'''

import os
from posixpath import dirname
from Core_V_V3 import *
from ObtainData import ObtainData


def __tmp__(ori_epc, filename):
    list_epc, list_time, list_phase, __ = ObtainData(
        ori_epc, filename=filename, antenna='9')
    plot_epc, __, __, __ = ObtainData(
        ori_epc, filename=filename, antenna='9')
    fit_epc, core_time, core_phase, l_list, r_list, dim_l_list, dim_r_list, unfit_epc = process(
        list_epc, list_time, list_phase)
    fit_phase, parameter = get_fit(fit_epc, core_time, core_phase)
    pos, order = get_order(fit_epc, parameter)

    if(len(parameter) > 10):
        core_time, core_phase = adapt_shape(fit_epc, list_time, list_phase, l_list,
                                            r_list, dim_l_list, dim_r_list, parameter)
        fit_phase, parameter = get_fit(fit_epc, core_time, core_phase)
        pos, order = get_order(fit_epc, parameter)
    return order


def save_plot(ori_epc, file, dirname):
    filename = os.path.join(dirname, file)
    list_epc, list_time, list_phase, __ = ObtainData(
        ori_epc, filename=filename, antenna='9')
    plot_epc, __, __, __ = ObtainData(
        ori_epc, filename=filename, antenna='9')

    fit_epc, core_time, core_phase, l_list, r_list, dim_l_list, dim_r_list, unfit_epc = process(
        list_epc, list_time, list_phase)
    fit_phase, parameter = get_fit(fit_epc, core_time, core_phase)
    pos, order = get_order(fit_epc, parameter)

    if(len(parameter) > 10):
        core_time, core_phase = adapt_shape(fit_epc, [list_time[list_epc.index(epc)] for epc in fit_epc], [list_phase[list_epc.index(epc)] for epc in fit_epc], l_list,
                                            r_list, dim_l_list, dim_r_list, parameter)
        fit_phase, parameter = get_fit(fit_epc, core_time, core_phase)
        pos, order = get_order(fit_epc, parameter)
        get_plot(os.path.join('tmp', file),  plot_epc, fit_epc, core_time, core_phase, fit_phase, list_time, list_phase,
                 pos, order, parameter, unfit_epc)


def main():
    ori_epc_one = '0f-1d'
    ori_epc_two = '2d-3b'
    order_one = ['15', '1D', '14', '1C', '13', '1B', '12',
                 '1A', '11', '19', '10', '18', '0F', '17', '16']
    order_two = ['2D', '2E', '2F', '30', '31', '32', '33',
                 '34', '35', '36', '37', '38', '39', '3A', '3B']
    dirname = r'data\2021-07-18'
    data_file = os.listdir(dirname)
    data_file.remove(r'155235-160612 right order.jpg')
    data_file.remove(r'162512-164408 right order.jpg')
    data_file.sort()

    right_ans = 0
    error_ans = 0
    wrong_ans = 0
    for i in range(len(data_file)):
        try:
            print(data_file[i], end=' ')
            if i < 40:
                if __tmp__(ori_epc_one, os.path.join(dirname, data_file[i])) == order_one:
                    right_ans += 1
                    print('right')
                else:
                    wrong_ans += 1
                    print('wrong')
                    save_plot(
                        ori_epc_one, data_file[i], dirname)
            else:
                if __tmp__(ori_epc_two, os.path.join(dirname, data_file[i])) == order_two:
                    right_ans += 1
                    print('right')
                else:
                    wrong_ans += 1
                    print('wrong')
                    save_plot(
                        ori_epc_two, data_file[i], dirname)
        except Exception as e:
            error_ans += 1
            print('error')
            print(e)

    print('right:', right_ans)
    print('wrong', wrong_ans)
    print('error', error_ans)
    print('right_rate', right_ans / len(data_file))


if __name__ == '__main__':
    main()
