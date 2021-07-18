'''
Author: xv_rong
Date: 2021-07-18 14:02:24
LastEditors: xv_rong
LastEditTime: 2021-07-18 15:06:18
Description:
FilePath: \RFID_FMS\pysrc\read_data.py
'''
import jpype
import os


def main():
    jarpath = os.path.join(os.path.abspath(
        "."), 'E:\\OneDrive\\Projects\\RFID\RFID_FMS\\lib\\RFID_FMS.jar')
    jvmPath = jpype.getDefaultJVMPath()
    jvmArg = '-Dhostname=SpeedwayR-12-BE-43'
    if not jpype.isJVMStarted():
        jpype.startJVM(jvmPath, jvmArg, "-ea",
                       "-Djava.class.path=%s" % (jarpath))
    javaClass = jpype.JClass('GetInfomationOfRssiAndPhase')
    if jpype.isJVMStarted():
        javaClass.start_reader()


if __name__ == '__main__':
    main()
