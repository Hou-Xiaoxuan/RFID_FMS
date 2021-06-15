import PhaseFitting
filename = "RFID/data002.txt"
with open(filename) as f:
    lines = f.readlines()
    data = [float(line.split('#')[-2]) for line in lines]  # 只取每一行数据的相位信息
    time = [float(line.split('#')[1]) for line in lines]
    time = list(range(0, len(data)))
    data_fit, center, parameter = PhaseFitting.PhaseFitting(time, data)
    PhaseFitting.visualization(data_fit)
    print("9")
