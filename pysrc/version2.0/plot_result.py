'''
Author: xv_rong
Date: 2021-09-24 13:27:54
LastEditors: xv_rong
LastEditTime: 2021-09-25 10:19:32
Description: 
FilePath: /RFID_FMS/pysrc/plot_result.py
'''
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
SHOW_FIG = True
SAVE_FIG = False


def plot_order(figname, plot_epc, fit_epc, core_time, core_phase, fit_phase, list_time, list_phase, pos, order, parameter, unfit_epc):
    colors = list(mcolors.TABLEAU_COLORS.keys())  # 颜色变化
    len_colors = len(mcolors.TABLEAU_COLORS)  # 颜色长度
    plt.figure(figname)
    plt.title("order is " + str(order) + " unfit:" +
              str([unfit_epc[num][7:9] for num in range(0, len(unfit_epc))]))

    for i in range(len(fit_epc)):
        if (fit_epc[i] in plot_epc):
            # plt.plot(core_time[i], fit_phase[i],
            #          color=mcolors.TABLEAU_COLORS[colors[i % len_colors]], marker='.', linestyle=':')
            plt.plot(core_time[i], fit_phase[i],
                     color=mcolors.TABLEAU_COLORS[colors[i % len_colors]])

            plt.scatter(list_time[i], list_phase[i],
                        color=mcolors.TABLEAU_COLORS[colors[i % len_colors]], marker='.')

    plt.legend([str(fit_epc[i][7:9]) + ' a:' + str(parameter[i][0])
               for i in range(len(fit_epc))], loc='upper right', fontsize='small')   # 设置图例
    for i in range(0, len(fit_epc)):
        if (fit_epc[i] in plot_epc):
            plt.plot([pos[i]] * 20, [i / 10 for i in range(0, 60, 3)],
                     color=mcolors.TABLEAU_COLORS[colors[i % len_colors]])
    if SAVE_FIG:
        plt.savefig('./' + figname + '.png', dpi=600)
        print('./' + figname + '.png' + ' saved')
    if SHOW_FIG:
        plt.show()
