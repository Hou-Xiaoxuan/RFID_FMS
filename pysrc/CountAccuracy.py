'''
Author: LinXuan
Date: 2021-07-18 17:48:11
Description: 计算完成准确率
LastEditors: LinXuan
LastEditTime: 2021-07-18 18:50:07
FilePath: \RFID\pysrc\CountAccuracy.py
'''


from Core_V_V3 import GetOrder


def main():
    success = 0
    rightorder1 = ['15', '1D', '14', '1C', '13',
                   '1B', '12', '1A', '11', '19',
                   '10', '18', '0F', '17', '16']
    rightorder2 = ['2D', '2E', '2F', '30', '31',
                   '32', '33', '34', '35', '36',
                   '37', '38', '39', '3A', '3B']
    with open("Data/2021-07-18/alldata.txt") as allfile:
        cnt = 0
        dirpath = "Data/2021-07-18/"
        for filename in allfile:
            filename = filename.replace("\n", '')
            cnt += 1
            flag = 0
            try:
                if(cnt <= 40 and GetOrder("0F-1D", filename=dirpath + filename, antenna='9') == rightorder1):
                    flag = 1
                if(cnt > 40 and GetOrder("2C-3B", filename=dirpath + filename, antenna='9') == rightorder2):
                    flag = 1
                if(flag == 1):
                    success += 1
                print(cnt, ' ', filename, ": ", flag)
            except:
                print(cnt, ' ', filename, ": ", "错误")
        print("正确率为: ", success / 80)


if __name__ == "__main__":
    main()
