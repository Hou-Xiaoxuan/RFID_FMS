'''
@Time    : 2021/06/28
@Author  : LinXuan
@File    : ObtainData
@Function: 获取原始数据
'''
import re


def GenerateListenEpc(params):
    '''
    @params         : 任意指定的最长8位的EPC号码
    @function       : 生成实验的标签监听列表
    '''
    listen_epc = []
    for ite in params:
        param = str(ite)
        if(param.find('-') == -1):
            # 处理指定传参
            temp_list = re.split(",| ", param)  # 以',' ' ' 分割
            temp_list = [i for i in temp_list if i != '']  # 去除空
            temp_list = [int(i, 16) for i in temp_list]  # 转16进制int
            temp_list = [str(hex(i))[2:len(hex(i))] for i in temp_list]  # 转回str，去除前缀0
            temp_list = ['0' * (8 - len(i)) + i for i in temp_list]  # 补0
            temp_list = [i[0:4].upper() + ' ' + i[4:8].upper() for i in temp_list]  # 补空格，转大写
            # listen_epc.append(*temp_list)
            for st in temp_list:
                listen_epc.append(st)
        else:
            # 处理范围传参
            # if(param.split('-') > 2):
            #     print("Wrong Type parameter")
            #     return []
            left, right = param.split('-')
            if(left > right):
                print("left not less than eight")
                return []
            l = int(left, 16)
            while(l <= int(right, 16)):
                temp = str(hex(l)[2:len(str(hex(l)))])  # 去前缀
                temp = '0' * (8 - len(temp)) + temp  # 补0
                temp = temp[0:4] + ' ' + temp[4:8]  # 补空格
                listen_epc.append(temp.upper())
                l += 1

    return listen_epc


def ObtainData(*params, filename="./data.txt", antenna="1,17"):
    '''
    @params         : 任意指定的最长8位的EPC号码
    @function       : 返回实验需要的数据
    '''
    list_epc = []
    list_time = []           # Time列表
    list_rssi = []           # RSSI列表
    list_phase = []          # PHASE列表
    first_time = 0           # 初始化一个开始时间，每次获得的开始时间不同

    list_antenna = re.split(",| ", antenna)
    list_antenna = [i for i in list_antenna if i != '']  # 去除空
    listen_epc = GenerateListenEpc(params)

    with open(filename) as lines:
        for line in lines:
            tag_info = line.split('#')
            if len(tag_info) != 5:                          # 接收的TagInfo长度为4，分别为EPC, Time, Rssi, Phase，错误则开启下一个循环
                continue
            elif tag_info[0][0:9] not in listen_epc:        # 筛选在监听列表中的epc号（仅识别前9位
                continue
            elif tag_info[4][0:-1] not in list_antenna:           # 筛选监听列表中的天线号（去除tag_info[4]中的\n
                continue
            else:
                if first_time == 0:                         # 第一次接收到Tag信息，将FirstTime初始化
                    first_time = int(tag_info[1])
                if tag_info[0] not in list_epc:             # 若出现新标签，将新标签加入列表，为新标签创建各信息列表
                    list_epc.append(tag_info[0])
                    list_time.append([])
                    list_rssi.append([])
                    list_phase.append([])
                tag_index = list_epc.index(tag_info[0])     # 找出当前Tag所处列表位置

                # 将相应Tag信息入列表
                list_time[tag_index].append(
                    (int(tag_info[1]) - first_time) / 1000000)        # 对时间处理为精度0.1s
                list_rssi[tag_index].append(float(tag_info[2]))
                list_phase[tag_index].append(float(tag_info[3]))

    return list_epc, list_time, list_phase, list_rssi


def main():
    ObtainData("0F 1D", filename="./Data/2021-06-28/20-08-15.txt")


if __name__ == "__main__":
    main()
